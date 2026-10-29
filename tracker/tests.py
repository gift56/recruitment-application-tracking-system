from datetime import datetime, timezone
from io import BytesIO
from zipfile import ZipFile

from django.contrib import admin as django_admin
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase

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
