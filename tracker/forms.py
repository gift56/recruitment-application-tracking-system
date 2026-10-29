from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction

from .models import (
    Application,
    Candidate,
    Department,
    InterviewNote,
    JobPosting,
    validate_resume_file,
)


FORM_CONTROL_CLASSES = (
    'mt-1 block w-full rounded-xl border border-slate-300 bg-white '
    'px-3 py-2.5 text-sm text-slate-900 shadow-sm focus:border-indigo-500 '
    'focus:outline-none focus:ring-2 focus:ring-indigo-200'
)


def style_form_fields(form):
    for field_name, field in form.fields.items():
        field.widget.attrs['class'] = FORM_CONTROL_CLASSES
        field_id = form[field_name].id_for_label
        described_by = []
        if field.help_text:
            described_by.append(f'{field_id}-help')
        if form.is_bound and form.errors.get(field_name):
            field.widget.attrs['aria-invalid'] = 'true'
            described_by.append(f'{field_id}-errors')
        if described_by:
            field.widget.attrs['aria-describedby'] = ' '.join(described_by)


class RecruiterAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)


class ApplicationForm(forms.ModelForm):
    full_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone = forms.CharField(max_length=32, required=False)
    resume = forms.FileField(required=False, validators=[validate_resume_file])
    portfolio_url = forms.URLField(max_length=200, required=False)

    class Meta:
        model = Application
        fields = [
            'full_name',
            'email',
            'phone',
            'resume',
            'portfolio_url',
            'cover_letter',
        ]
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resume'].help_text = 'PDF or DOCX only; maximum file size 5 MiB.'
        style_form_fields(self)

    def save(self, commit=True):
        application = super().save(commit=False)
        candidate = Candidate(
            full_name=self.cleaned_data['full_name'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            resume=self.cleaned_data.get('resume'),
            portfolio_url=self.cleaned_data['portfolio_url'],
        )
        application.candidate = candidate

        if commit:
            with transaction.atomic():
                candidate.save()
                application.save()

        return application


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            'title',
            'department',
            'location',
            'salary_range',
            'description',
            'requirements',
            'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'requirements': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['salary_range'].required = True
        self.fields['salary_range'].help_text = (
            'Enter a compensation range to display on the public job board.'
        )
        style_form_fields(self)


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        duplicate_departments = Department.objects.filter(name__iexact=name)
        if self.instance.pk:
            duplicate_departments = duplicate_departments.exclude(
                pk=self.instance.pk
            )
        if duplicate_departments.exists():
            raise forms.ValidationError(
                'A department with this name already exists.'
            )
        return name


class InterviewNoteForm(forms.ModelForm):
    class Meta:
        model = InterviewNote
        fields = ['rating', 'notes']
        widgets = {
            'rating': forms.Select(),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)
