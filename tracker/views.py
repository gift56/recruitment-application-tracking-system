from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import ApplicationForm
from .models import Department, JobPosting


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
