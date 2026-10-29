from django import forms
from django.db import transaction

from .models import Application, Candidate, validate_resume_file


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
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = (
                'mt-1 block w-full rounded-xl border border-slate-300 bg-white '
                'px-3 py-2.5 text-sm text-slate-900 shadow-sm focus:border-indigo-500 '
                'focus:outline-none focus:ring-2 focus:ring-indigo-200'
            )
            if self.is_bound and self.errors.get(field_name):
                field.widget.attrs['aria-invalid'] = 'true'
                field.widget.attrs['aria-describedby'] = f'{field_name}-errors'

        self.fields['resume'].help_text = 'PDF or DOCX only; maximum file size 5 MiB.'

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
