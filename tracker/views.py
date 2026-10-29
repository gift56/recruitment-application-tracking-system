from pathlib import PurePath

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    ApplicationForm,
    DepartmentForm,
    InterviewNoteForm,
    JobPostingForm,
    RecruiterAuthenticationForm,
)
from .models import Application, Department, JobPosting


class HomeView(TemplateView):
    template_name = 'tracker/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_jobs'] = (
            JobPosting.objects.filter(status=JobPosting.Status.ACTIVE)
            .select_related('department')
            .order_by('-created_at')[:4]
        )
        return context


class RecruiterLoginView(LoginView):
    template_name = 'tracker/login.html'
    next_page = 'tracker:recruiter_dashboard'
    form_class = RecruiterAuthenticationForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('tracker:login')

    def test_func(self):
        return self.request.user.is_staff


class RecruiterDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'tracker/recruiter_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            total_applicants=Application.objects.count(),
            active_postings=JobPosting.objects.filter(
                status=JobPosting.Status.ACTIVE
            ).count(),
            candidates_in_interview=Application.objects.filter(
                status=Application.Status.INTERVIEW
            ).count(),
            hired_count=Application.objects.filter(
                status=Application.Status.HIRED
            ).count(),
        )
        return context


class JobPostingCreateView(StaffRequiredMixin, CreateView):
    form_class = JobPostingForm
    template_name = 'tracker/job_form.html'
    success_url = reverse_lazy('tracker:recruiter_dashboard')

    def form_valid(self, form):
        messages.success(
            self.request,
            'Job posting created successfully.',
        )
        return super().form_valid(form)


class DepartmentCreateView(StaffRequiredMixin, CreateView):
    form_class = DepartmentForm
    template_name = 'tracker/department_form.html'
    success_url = reverse_lazy('tracker:recruiter_job_create')

    def form_valid(self, form):
        messages.success(self.request, 'Department created successfully.')
        return super().form_valid(form)


class RecruiterJobListView(StaffRequiredMixin, ListView):
    model = JobPosting
    template_name = 'tracker/recruiter_job_list.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        return (
            JobPosting.objects.select_related('department')
            .annotate(application_count=Count('applications'))
            .order_by('-created_at')
        )


class JobPostingUpdateView(StaffRequiredMixin, UpdateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'tracker/job_form.html'
    success_url = reverse_lazy('tracker:recruiter_jobs')

    def get_queryset(self):
        return super().get_queryset().select_related('department')

    def form_valid(self, form):
        messages.success(self.request, 'Job posting updated successfully.')
        return super().form_valid(form)


class JobPostingDeleteView(StaffRequiredMixin, View):
    template_name = 'tracker/job_confirm_delete.html'

    def get_job(self):
        return get_object_or_404(
            JobPosting.objects.select_related('department').annotate(
                application_count=Count('applications')
            ),
            pk=self.kwargs['pk'],
        )

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {'job': self.get_job()},
        )

    def post(self, request, *args, **kwargs):
        job = self.get_job()
        if job.application_count:
            messages.error(
                request,
                'This job has applications and cannot be deleted. '
                'Mark it Inactive to retain its application history.',
            )
            return redirect('tracker:recruiter_jobs')

        try:
            job.delete()
        except ProtectedError:
            messages.error(
                request,
                'This job now has applications and cannot be deleted. '
                'Mark it Inactive to retain its application history.',
            )
            return redirect('tracker:recruiter_jobs')

        messages.success(request, 'Job posting deleted.')
        return redirect('tracker:recruiter_jobs')


def _application_pipeline_queryset():
    return Application.objects.select_related(
        'candidate',
        'job_posting',
        'job_posting__department',
    ).order_by('-applied_at')


class RecruiterApplicationListView(StaffRequiredMixin, ListView):
    model = Application
    template_name = 'tracker/application_pipeline.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return _application_pipeline_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for application in context['applications']:
            application.note_form = InterviewNoteForm(
                prefix=f'note-{application.pk}'
            )
        context['application_statuses'] = Application.Status.choices
        return context


class ApplicationStatusUpdateView(StaffRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(Application, pk=pk)
        status = request.POST.get('status', '')
        if status not in Application.Status.values:
            messages.error(request, 'Choose a valid application status.')
            return self._redirect_to_pipeline()

        application.status = status
        application.save(update_fields=['status'])
        messages.success(request, 'Application status updated.')
        return self._redirect_to_pipeline()

    @staticmethod
    def _redirect_to_pipeline():
        return redirect('tracker:recruiter_applications')


class InterviewNoteCreateView(StaffRequiredMixin, FormView):
    form_class = InterviewNoteForm
    template_name = 'tracker/application_pipeline.html'

    def get_application(self):
        if not hasattr(self, '_application'):
            self._application = get_object_or_404(
                Application.objects.select_related('candidate', 'job_posting'),
                pk=self.kwargs['pk'],
            )
        return self._application

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['prefix'] = f'note-{self.get_application().pk}'
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_application = self.get_application()
        applications = list(_application_pipeline_queryset())
        for pipeline_application in applications:
            pipeline_application.note_form = (
                context['form']
                if pipeline_application.pk == target_application.pk
                else InterviewNoteForm(prefix=f'note-{pipeline_application.pk}')
            )
        context['applications'] = applications
        context['application_statuses'] = Application.Status.choices
        return context

    def form_valid(self, form):
        note = form.save(commit=False)
        note.application = self.get_application()
        note.interviewer_name = (
            self.request.user.get_full_name().strip()
            or self.request.user.get_username()
        )
        note.scheduled_at = timezone.now()
        note.save()
        messages.success(self.request, 'Interview note saved.')
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('tracker:recruiter_applications')


class ApplicationResumeView(StaffRequiredMixin, View):
    def get(self, request, pk):
        application = get_object_or_404(
            Application.objects.select_related('candidate'),
            pk=pk,
        )
        resume = application.candidate.resume
        if not resume:
            raise Http404

        extension = PurePath(resume.name).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': (
                'application/vnd.openxmlformats-officedocument.'
                'wordprocessingml.document'
            ),
        }
        content_type = content_types.get(extension)
        if content_type is None:
            raise Http404

        try:
            file_handle = resume.open('rb')
        except FileNotFoundError as error:
            raise Http404 from error

        return FileResponse(
            file_handle,
            as_attachment=extension != '.pdf',
            filename=PurePath(resume.name).name,
            content_type=content_type,
        )


class JobListView(ListView):
    model = JobPosting
    template_name = 'tracker/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 12

    def get_queryset(self):
        queryset = (
            JobPosting.objects.filter(status=JobPosting.Status.ACTIVE)
            .select_related('department')
            .order_by('-created_at')
        )
        self.search_query = self.request.GET.get('q', '').strip()
        if self.search_query:
            queryset = queryset.filter(
                Q(title__icontains=self.search_query)
                | Q(location__icontains=self.search_query)
            )

        self.selected_department = self.request.GET.get('department', '').strip()
        if self.selected_department:
            try:
                department_id = int(self.selected_department)
            except ValueError:
                return queryset.none()
            if department_id < 1:
                return queryset.none()
            queryset = queryset.filter(department_id=department_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(
            job_postings__status=JobPosting.Status.ACTIVE
        ).distinct()
        context['search_query'] = getattr(
            self, 'search_query', self.request.GET.get('q', '').strip()
        )
        context['selected_department'] = getattr(
            self, 'selected_department', self.request.GET.get('department', '').strip()
        )
        return context


class JobDetailView(DetailView):
    model = JobPosting
    template_name = 'tracker/job_detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(status=JobPosting.Status.ACTIVE)
            .select_related('department')
        )


class ApplicationCreateView(CreateView):
    form_class = ApplicationForm
    template_name = 'tracker/apply.html'

    def dispatch(self, request, *args, **kwargs):
        self.job_posting = get_object_or_404(
            JobPosting.objects.filter(
                status=JobPosting.Status.ACTIVE
            ).select_related('department'),
            pk=kwargs['pk'],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = self.job_posting
        return context

    def form_valid(self, form):
        form.instance.job_posting = self.job_posting
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Your application for {self.job_posting.title} was submitted successfully.',
        )
        return response

    def get_success_url(self):
        return reverse('tracker:job_detail', kwargs={'pk': self.job_posting.pk})
