from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tracker.models import Department, JobPosting


class Command(BaseCommand):
    help = 'Create local development departments, sample jobs, and a recruiter account.'

    departments = ('Engineering', 'Product', 'Design')
    sample_jobs = (
        {
            'title': 'Backend Engineer',
            'department': 'Engineering',
            'location': 'Remote',
            'salary_range': '$120,000-$160,000 per year',
            'description': 'Build and maintain reliable recruitment tools.',
            'requirements': 'Experience building web applications.',
        },
        {
            'title': 'Product Designer',
            'department': 'Product',
            'location': 'Hybrid',
            'salary_range': '$100,000-$135,000 per year',
            'description': 'Design clear and accessible product experiences.',
            'requirements': 'Experience with user-centered product design.',
        },
        {
            'title': 'UX Designer',
            'department': 'Design',
            'location': 'Remote',
            'salary_range': '$95,000-$130,000 per year',
            'description': 'Help teams make candidate journeys easier to use.',
            'requirements': 'Experience designing responsive interfaces.',
        },
    )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                'seed_data is for local development only and requires DEBUG=True.'
            )

        user_model = get_user_model()
        with transaction.atomic():
            recruiter = user_model.objects.filter(username='recruiter').first()
            if recruiter is not None and not recruiter.is_staff:
                raise CommandError(
                    "The existing 'recruiter' account is not staff; "
                    'seed_data will not change its permissions.'
                )

            departments = {
                name: Department.objects.get_or_create(name=name)[0]
                for name in self.departments
            }

            for job_data in self.sample_jobs:
                defaults = {
                    'location': job_data['location'],
                    'salary_range': job_data['salary_range'],
                    'description': job_data['description'],
                    'requirements': job_data['requirements'],
                    'status': JobPosting.Status.ACTIVE,
                }
                job, _ = JobPosting.objects.get_or_create(
                    title=job_data['title'],
                    department=departments[job_data['department']],
                    defaults=defaults,
                )
                if not job.salary_range:
                    job.salary_range = job_data['salary_range']
                    job.save(update_fields=['salary_range'])

            if recruiter is None:
                recruiter = user_model(username='recruiter', is_staff=True)
                recruiter.set_password('password123')
                recruiter.save()

        self.stdout.write(
            self.style.SUCCESS(
                'Development seed data is ready: Engineering, Product, and Design; '
                'three active sample jobs; recruiter account created or preserved.'
            )
        )
