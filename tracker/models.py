from io import BytesIO
from pathlib import PurePath
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


MAX_RESUME_SIZE = 5 * 1024 * 1024
ALLOWED_RESUME_EXTENSIONS = {'.pdf', '.docx'}


def resume_upload_to(instance, filename):
    extension = PurePath(filename).suffix.lower()
    return f'resumes/{uuid4().hex}{extension}'


def validate_resume_file(uploaded_file):
    extension = PurePath(uploaded_file.name).suffix.lower()
    if extension not in ALLOWED_RESUME_EXTENSIONS:
        raise ValidationError('Resume must be a PDF or DOCX file.')

    if uploaded_file.size > MAX_RESUME_SIZE:
        raise ValidationError('Resume must be no larger than 5 MiB.')

    file_obj = getattr(uploaded_file, 'file', uploaded_file)
    position = file_obj.tell()
    try:
        file_obj.seek(0)
        content = file_obj.read(MAX_RESUME_SIZE + 1)
    finally:
        file_obj.seek(position)

    if extension == '.pdf':
        if not content.startswith(b'%PDF-') or b'%%EOF' not in content[-1024:]:
            raise ValidationError('The uploaded file is not a valid PDF document.')
        return

    try:
        with ZipFile(BytesIO(content)) as archive:
            if 'word/document.xml' not in archive.namelist():
                raise ValidationError('The uploaded file is not a valid DOCX document.')
    except BadZipFile as error:
        raise ValidationError('The uploaded file is not a valid DOCX document.') from error


class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    title = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='job_postings',
    )
    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at'], name='job_status_created_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=['active', 'inactive']),
                name='job_status_valid',
            ),
        ]

    def __str__(self):
        return self.title


class Candidate(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    resume = models.FileField(
        upload_to=resume_upload_to,
        validators=[validate_resume_file],
        blank=True,
    )
    portfolio_url = models.URLField(blank=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} ({self.email})'


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = 'applied', 'Applied'
        SCREENING = 'screening', 'Screening'
        INTERVIEW = 'interview', 'Interview'
        OFFER = 'offer', 'Offer'
        HIRED = 'hired', 'Hired'
        REJECTED = 'rejected', 'Rejected'

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.PROTECT,
        related_name='applications',
    )
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.PROTECT,
        related_name='applications',
        db_index=False,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.APPLIED,
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True)

    class Meta:
        ordering = ['-applied_at']
        indexes = [
            models.Index(
                fields=['status', '-applied_at'],
                name='app_status_applied_idx',
            ),
            models.Index(
                fields=['job_posting', 'status'],
                name='app_job_status_idx',
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        'applied',
                        'screening',
                        'interview',
                        'offer',
                        'hired',
                        'rejected',
                    ]
                ),
                name='application_status_valid',
            ),
        ]

    def __str__(self):
        return f'{self.candidate} - {self.job_posting} ({self.get_status_display()})'


class InterviewNote(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interview_notes',
        db_index=False,
    )
    interviewer_name = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    notes = models.TextField(blank=True)
    scheduled_at = models.DateTimeField()

    class Meta:
        ordering = ['scheduled_at']
        indexes = [
            models.Index(
                fields=['application', 'scheduled_at'],
                name='note_app_scheduled_idx',
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name='interview_rating_1_to_5',
            ),
        ]

    def __str__(self):
        return f'Interview note for {self.application} ({self.scheduled_at:%Y-%m-%d %H:%M})'
