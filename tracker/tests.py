from datetime import datetime, timedelta, timezone
from io import BytesIO
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from zipfile import ZipFile

from django.contrib import admin as django_admin
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages import constants as message_constants
from django.contrib.messages.storage.base import Message
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.template.loader import render_to_string
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .admin import (
    APPLICATION_STATUS_STYLES,
    ApplicationAdmin,
    InterviewNoteInline,
)
from .models import (
    MAX_RESUME_SIZE,
    Application,
    Candidate,
    Department,
    InterviewNote,
    JobPosting,
    resume_upload_to,
    validate_resume_file,
)


def make_docx_file(name='resume.docx'):
    content = BytesIO()
    with ZipFile(content, 'w') as archive:
        archive.writestr('word/document.xml', '<document/>')
    return SimpleUploadedFile(name, content.getvalue())


class RecruitmentTemplateTests(SimpleTestCase):
    def test_base_template_renders_semantic_shell_without_feature_routes(self):
        rendered = render_to_string(
            'tracker/base.html',
            {
                'request': SimpleNamespace(user=AnonymousUser()),
                'messages': [],
            },
        )

        for landmark in ('<header', '<nav', '<main', '<footer'):
            with self.subTest(landmark=landmark):
                self.assertIn(landmark, rendered)
        self.assertIn('RecruiterHub', rendered)
        self.assertIn('[data-dismiss-alert]', rendered)
        self.assertIn('href="/"', rendered)
        self.assertIn('href="/jobs/"', rendered)
        self.assertNotIn('/recruiter/', rendered)

    def test_staff_navigation_links_to_existing_admin_route(self):
        rendered = render_to_string(
            'tracker/partials/navbar.html',
            {'request': SimpleNamespace(user=User(username='staff', is_staff=True))},
        )

        self.assertIn('href="/admin/"', rendered)
        self.assertIn('staff', rendered)

    def test_status_badges_cover_every_application_stage(self):
        styles = {
            Application.Status.APPLIED: 'border-blue-200 bg-blue-50 text-blue-700',
            Application.Status.SCREENING: 'border-purple-200 bg-purple-50 text-purple-700',
            Application.Status.INTERVIEW: 'border-amber-200 bg-amber-50 text-amber-700',
            Application.Status.OFFER: 'border-indigo-200 bg-indigo-50 text-indigo-700',
            Application.Status.HIRED: 'border-emerald-200 bg-emerald-50 text-emerald-700',
            Application.Status.REJECTED: 'border-rose-200 bg-rose-50 text-rose-700',
        }

        for status, label in Application.Status.choices:
            with self.subTest(status=status):
                rendered = render_to_string(
                    'tracker/partials/status_badge.html',
                    {'status': status, 'status_label': label},
                )
                for style in styles[status].split():
                    self.assertIn(style, rendered)
                self.assertIn(f'>{label}</span>', rendered)

    def test_status_badge_escapes_unknown_values_and_uses_neutral_style(self):
        malicious_status = '<img src=x onerror=alert(1)>'
        rendered = render_to_string(
            'tracker/partials/status_badge.html',
            {'status': malicious_status},
        )

        for style in ('border-slate-200', 'bg-slate-100', 'text-slate-700'):
            self.assertIn(style, rendered)
        self.assertIn('&lt;img', rendered)
        self.assertNotIn('<img', rendered)

    def test_alerts_render_each_message_level_accessibly(self):
        cases = (
            (message_constants.SUCCESS, 'bg-emerald-50', 'role="status"'),
            (message_constants.ERROR, 'bg-rose-50', 'role="alert"'),
            (message_constants.WARNING, 'bg-amber-50', 'role="status"'),
            (message_constants.INFO, 'bg-sky-50', 'role="status"'),
        )

        for level, style, role in cases:
            with self.subTest(level=level):
                rendered = render_to_string(
                    'tracker/partials/alerts.html',
                    {'messages': [Message(level, 'A notification')]},
                )
                self.assertIn(style, rendered)
                self.assertIn(role, rendered)
                self.assertIn('data-dismiss-alert', rendered)

    def test_alert_message_is_autoescaped(self):
        rendered = render_to_string(
            'tracker/partials/alerts.html',
            {'messages': [Message(message_constants.INFO, '<script>alert(1)</script>')]},
        )

        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('<script>alert(1)</script>', rendered)


class RecruitmentHomeViewTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Engineering')

    def test_root_renders_home_page_with_recent_active_jobs(self):
        jobs = []
        for index in range(5):
            job = JobPosting.objects.create(
                title=f'Engineer {index}',
                department=self.department,
                location='Remote',
                description='Build software.',
            )
            JobPosting.objects.filter(pk=job.pk).update(
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
                + timedelta(days=index)
            )
            jobs.append(job)
        inactive_job = JobPosting.objects.create(
            title='Inactive Engineer',
            department=self.department,
            location='Remote',
            description='Not open.',
            status=JobPosting.Status.INACTIVE,
        )

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/home.html')
        self.assertContains(response, 'Featured / Recent Jobs')
        self.assertContains(response, 'Browse All Jobs')
        for job in jobs[1:]:
            self.assertContains(response, job.title)
        self.assertNotContains(response, jobs[0].title)
        self.assertNotContains(response, inactive_job.title)

    def test_home_view_only_accepts_get_requests(self):
        response = self.client.post('/')

        self.assertEqual(response.status_code, 405)

    def test_root_and_tracker_namespaces_resolve_without_disrupting_admin(self):
        self.assertEqual(reverse('tracker:home'), '/')
        self.assertEqual(reverse('tracker_app:home'), '/tracker/')
        self.assertEqual(reverse('admin:index'), '/admin/')

        tracker_response = self.client.get('/tracker/')
        self.assertEqual(tracker_response.status_code, 200)


class PublicJobBoardViewTests(TestCase):
    def setUp(self):
        self.engineering = Department.objects.create(name='Engineering')
        self.design = Department.objects.create(name='Design')

    def create_job(self, title, department=None, **kwargs):
        return JobPosting.objects.create(
            title=title,
            department=department or self.engineering,
            location=kwargs.pop('location', 'Remote'),
            description=kwargs.pop('description', 'Build useful products.'),
            **kwargs,
        )

    def test_job_list_filters_by_search_and_department(self):
        matching = self.create_job(
            'Backend Engineer',
            location='London',
        )
        self.create_job('Product Designer', department=self.design)
        self.create_job('Frontend Engineer', department=self.design)
        self.create_job(
            'Inactive Engineer',
            status=JobPosting.Status.INACTIVE,
        )

        response = self.client.get(
            reverse('tracker:job_list'),
            {'q': 'engineer', 'department': self.engineering.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, matching.title)
        self.assertNotContains(response, 'Product Designer')
        self.assertNotContains(response, 'Frontend Engineer')
        self.assertNotContains(response, 'Inactive Engineer')

    def test_job_list_search_matches_location_and_invalid_department_is_safe(self):
        matching = self.create_job('Platform Specialist', location='Toronto')
        response = self.client.get(reverse('tracker:job_list'), {'q': 'toronto'})
        self.assertContains(response, matching.title)

        response = self.client.get(
            reverse('tracker:job_list'),
            {'department': 'not-a-number'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No matching jobs found')

    def test_job_list_paginates_and_preserves_filters(self):
        for index in range(13):
            self.create_job(f'Engineer {index}')

        response = self.client.get(
            reverse('tracker:job_list'),
            {'q': 'engineer', 'department': self.engineering.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['jobs']), 12)
        self.assertContains(
            response,
            f'?page=2&amp;q=engineer&amp;department={self.engineering.pk}',
        )
        self.assertEqual(
            response.context['departments'].get(),
            self.engineering,
        )

    def test_job_list_and_home_render_empty_states(self):
        response = self.client.get(reverse('tracker:job_list'))
        self.assertContains(response, 'No matching jobs found')

        response = self.client.get('/')
        self.assertContains(response, 'No open jobs right now')

    def test_inactive_jobs_are_not_publicly_viewable_or_applicable(self):
        inactive_job = self.create_job(
            'Closed role',
            status=JobPosting.Status.INACTIVE,
        )

        detail_response = self.client.get(
            reverse('tracker:job_detail', kwargs={'pk': inactive_job.pk})
        )
        application_response = self.client.get(
            reverse('tracker:application_create', kwargs={'pk': inactive_job.pk})
        )

        self.assertEqual(detail_response.status_code, 404)
        self.assertEqual(application_response.status_code, 404)

    def test_active_job_detail_contains_role_information_and_apply_action(self):
        job = self.create_job(
            'Accessibility Engineer',
            location='Remote',
            salary_range='$100k-$120k',
            requirements='Experience with accessible interfaces.',
        )

        response = self.client.get(
            reverse('tracker:job_detail', kwargs={'pk': job.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, job.title)
        self.assertContains(response, self.engineering.name)
        self.assertContains(response, job.location)
        self.assertContains(response, job.salary_range)
        self.assertContains(response, job.requirements)
        self.assertContains(
            response,
            reverse('tracker:application_create', kwargs={'pk': job.pk}),
        )

    def test_application_form_includes_csrf_and_multipart_encoding(self):
        job = self.create_job('Systems Engineer')

        response = self.client.get(
            reverse('tracker:application_create', kwargs={'pk': job.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="resume"')

    def test_anonymous_application_creates_linked_candidate_and_application(self):
        job = self.create_job('Software Engineer')
        client = Client(enforce_csrf_checks=True)
        url = reverse('tracker:application_create', kwargs={'pk': job.pk})
        get_response = client.get(url)
        csrf_token = get_response.cookies['csrftoken'].value

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = client.post(
                    url,
                    {
                        'full_name': 'Taylor Candidate',
                        'email': 'taylor@example.com',
                        'phone': '555-0100',
                        'portfolio_url': 'https://example.com/portfolio',
                        'cover_letter': 'I am excited to apply.',
                    },
                    HTTP_X_CSRFTOKEN=csrf_token,
                    follow=True,
                )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your application for Software Engineer was submitted successfully.')
        candidate = Candidate.objects.get(email='taylor@example.com')
        application = Application.objects.get(candidate=candidate)
        self.assertEqual(candidate.full_name, 'Taylor Candidate')
        self.assertEqual(candidate.phone, '555-0100')
        self.assertEqual(candidate.portfolio_url, 'https://example.com/portfolio')
        self.assertEqual(application.job_posting, job)
        self.assertEqual(application.cover_letter, 'I am excited to apply.')
        self.assertEqual(application.status, Application.Status.APPLIED)

    def test_application_accepts_valid_docx_resume(self):
        job = self.create_job('Document Specialist')
        url = reverse('tracker:application_create', kwargs={'pk': job.pk})

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    url,
                    {
                        'full_name': 'Morgan Candidate',
                        'email': 'morgan@example.com',
                        'resume': make_docx_file(),
                    },
                )

        self.assertEqual(response.status_code, 302)
        candidate = Candidate.objects.get(email='morgan@example.com')
        self.assertTrue(candidate.resume.name.endswith('.docx'))

    def test_invalid_application_fields_and_resumes_do_not_create_records(self):
        job = self.create_job('Secure Upload Engineer')
        url = reverse('tracker:application_create', kwargs={'pk': job.pk})
        invalid_submissions = [
            {
                'full_name': '',
                'email': 'not-an-email',
            },
            {
                'full_name': 'Invalid Extension',
                'email': 'extension@example.com',
                'resume': SimpleUploadedFile('resume.txt', b'not a document'),
            },
            {
                'full_name': 'Invalid PDF',
                'email': 'pdf@example.com',
                'resume': SimpleUploadedFile('resume.pdf', b'not a PDF'),
            },
            {
                'full_name': 'Invalid DOCX',
                'email': 'docx@example.com',
                'resume': SimpleUploadedFile('resume.docx', b'not a ZIP archive'),
            },
            {
                'full_name': 'Oversized Resume',
                'email': 'large@example.com',
                'resume': SimpleUploadedFile(
                    'resume.pdf',
                    b'%PDF-' + b'x' * (MAX_RESUME_SIZE + 1),
                ),
            },
        ]

        for submission in invalid_submissions:
            with self.subTest(email=submission.get('email')):
                response = self.client.post(url, submission)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].errors)
                self.assertEqual(Candidate.objects.count(), 0)
                self.assertEqual(Application.objects.count(), 0)


class RecruitmentAdminTests(SimpleTestCase):
    def test_all_tracker_models_are_registered_with_list_configuration(self):
        models = (Department, JobPosting, Candidate, Application, InterviewNote)

        for model in models:
            with self.subTest(model=model.__name__):
                model_admin = django_admin.site._registry[model]
                self.assertTrue(model_admin.list_display)
                self.assertTrue(model_admin.list_filter)
                self.assertTrue(model_admin.search_fields)

    def test_application_admin_includes_interview_note_inline(self):
        application_admin = django_admin.site._registry[Application]

        self.assertIn(InterviewNoteInline, application_admin.inlines)

    def test_status_badges_cover_every_application_stage(self):
        application_admin = ApplicationAdmin(Application, django_admin.site)
        expected_labels = {
            Application.Status.APPLIED: 'Applied',
            Application.Status.SCREENING: 'Screening',
            Application.Status.INTERVIEW: 'Interview',
            Application.Status.OFFER: 'Offer',
            Application.Status.HIRED: 'Hired',
            Application.Status.REJECTED: 'Rejected',
        }

        for status, label in expected_labels.items():
            with self.subTest(status=status):
                badge = str(
                    application_admin.status_badge(
                        Application(status=status),
                    )
                )

                self.assertIn(label, badge)
                self.assertIn(APPLICATION_STATUS_STYLES[status], badge)

    def test_status_badge_escapes_unexpected_status(self):
        application_admin = ApplicationAdmin(Application, django_admin.site)
        badge = str(
            application_admin.status_badge(
                Application(status='<img src=x onerror=alert(1)>'),
            )
        )

        self.assertIn('&lt;img', badge)
        self.assertNotIn('<img', badge)
        self.assertIn('background-color: #e5e7eb;', badge)


class RecruitmentModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name='Engineering')
        self.job = JobPosting.objects.create(
            title='Software Engineer',
            department=self.department,
            location='Remote',
            description='Build software.',
        )
        self.candidate = Candidate.objects.create(
            full_name='Alex Candidate',
            email='alex@example.com',
        )

    def test_string_representations_and_relationships(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job_posting=self.job,
        )
        note = InterviewNote.objects.create(
            application=application,
            interviewer_name='Jordan Interviewer',
            rating=5,
            notes='Strong interview.',
            scheduled_at=datetime(2026, 10, 29, 10, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(str(self.department), 'Engineering')
        self.assertEqual(str(self.job), 'Software Engineer')
        self.assertEqual(str(self.candidate), 'Alex Candidate (alex@example.com)')
        self.assertEqual(
            str(application),
            'Alex Candidate (alex@example.com) - Software Engineer (Applied)',
        )
        self.assertIn('Interview note for', str(note))
        self.assertIs(application.candidate, self.candidate)
        self.assertIs(application.job_posting, self.job)
        self.assertIs(note.application, application)

    def test_status_choices_and_defaults(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job_posting=self.job,
        )

        self.assertEqual(self.job.status, JobPosting.Status.ACTIVE)
        self.assertEqual(application.status, Application.Status.APPLIED)
        self.assertEqual(
            [choice[0] for choice in Application.Status.choices],
            ['applied', 'screening', 'interview', 'offer', 'hired', 'rejected'],
        )

    def test_rating_validation_and_database_constraint(self):
        application = Application.objects.create(
            candidate=self.candidate,
            job_posting=self.job,
        )
        for rating in (1, 5):
            note = InterviewNote(
                application=application,
                interviewer_name='Jordan Interviewer',
                rating=rating,
                scheduled_at=datetime(2026, 10, 29, 10, 0, tzinfo=timezone.utc),
            )
            note.full_clean()
            note.save()

        for rating in (0, 6):
            with self.subTest(rating=rating):
                note = InterviewNote(
                    application=application,
                    interviewer_name='Jordan Interviewer',
                    rating=rating,
                    scheduled_at=datetime(2026, 10, 29, 10, 0, tzinfo=timezone.utc),
                )
                with self.assertRaises(ValidationError):
                    note.full_clean()

                with self.assertRaises(IntegrityError):
                    with transaction.atomic():
                        InterviewNote.objects.create(
                            application=application,
                            interviewer_name='Jordan Interviewer',
                            rating=rating,
                            scheduled_at=datetime(
                                2026, 10, 29, 10, 0, tzinfo=timezone.utc
                            ),
                        )

    def test_status_database_constraints(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                JobPosting.objects.create(
                    title='Invalid status job',
                    department=self.department,
                    location='Remote',
                    description='Test.',
                    status='invalid',
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Application.objects.create(
                    candidate=self.candidate,
                    job_posting=self.job,
                    status='invalid',
                )

    def test_resume_file_validation(self):
        pdf = SimpleUploadedFile(
            'resume.pdf',
            b'%PDF-1.7\nexample document\n%%EOF',
        )
        validate_resume_file(pdf)
        validate_resume_file(make_docx_file())

        cases = [
            SimpleUploadedFile('resume.txt', b'%PDF-1.7\n%%EOF'),
            SimpleUploadedFile('resume.pdf', b'not a PDF'),
            SimpleUploadedFile('resume.docx', b'not a ZIP archive'),
            SimpleUploadedFile('resume.pdf', b'%PDF-' + b'x' * MAX_RESUME_SIZE),
        ]
        for uploaded_file in cases:
            with self.subTest(name=uploaded_file.name):
                with self.assertRaises(ValidationError):
                    validate_resume_file(uploaded_file)

    def test_resume_upload_path_uses_generated_filename(self):
        path = resume_upload_to(self.candidate, '..\\candidate resume.PDF')

        self.assertTrue(path.startswith('resumes/'))
        self.assertTrue(path.endswith('.pdf'))
        self.assertNotIn('candidate', path)
        self.assertNotIn('..', path)
