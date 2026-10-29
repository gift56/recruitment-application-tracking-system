from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html

from .models import Application, Candidate, Department, InterviewNote, JobPosting

APPLICATION_STATUS_STYLES = {
    Application.Status.APPLIED: 'background-color: #e0f2fe; color: #1f2937;',
    Application.Status.SCREENING: 'background-color: #fef3c7; color: #1f2937;',
    Application.Status.INTERVIEW: 'background-color: #ede9fe; color: #1f2937;',
    Application.Status.OFFER: 'background-color: #dbeafe; color: #1f2937;',
    Application.Status.HIRED: 'background-color: #dcfce7; color: #1f2937;',
    Application.Status.REJECTED: 'background-color: #fee2e2; color: #1f2937;',
}
DEFAULT_STATUS_STYLE = 'background-color: #e5e7eb; color: #1f2937;'


class InterviewNoteInline(admin.TabularInline):
    model = InterviewNote
    fields = ('interviewer_name', 'rating', 'scheduled_at', 'notes')
    extra = 1


class CandidateAssetFilter(SimpleListFilter):
    title = 'candidate assets'
    parameter_name = 'asset'

    def lookups(self, request, model_admin):
        return (
            ('resume', 'Has resume'),
            ('no_resume', 'No resume'),
            ('portfolio', 'Has portfolio'),
            ('no_portfolio', 'No portfolio'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'resume':
            return queryset.exclude(resume='')
        if self.value() == 'no_resume':
            return queryset.filter(resume='')
        if self.value() == 'portfolio':
            return queryset.exclude(portfolio_url='')
        if self.value() == 'no_portfolio':
            return queryset.filter(portfolio_url='')
        return queryset


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'location', 'status', 'created_at')
    list_filter = ('department', 'status', 'created_at')
    search_fields = (
        'title',
        'location',
        'description',
        'requirements',
        'department__name',
    )
    list_select_related = ('department',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'portfolio_url')
    list_filter = (CandidateAssetFilter,)
    search_fields = ('full_name', 'email', 'phone')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job_posting', 'status_badge', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = (
        'candidate__full_name',
        'candidate__email',
        'job_posting__title',
    )
    list_select_related = ('candidate', 'job_posting')
    inlines = (InterviewNoteInline,)

    @admin.display(description='Stage', ordering='status')
    def status_badge(self, obj):
        style = APPLICATION_STATUS_STYLES.get(obj.status, DEFAULT_STATUS_STYLE)
        return format_html(
            '<span style="{}; padding: 0.2rem 0.5rem; border-radius: 9999px; '
            'font-weight: 600;">{}</span>',
            style,
            obj.get_status_display(),
        )


@admin.register(InterviewNote)
class InterviewNoteAdmin(admin.ModelAdmin):
    list_display = ('application', 'interviewer_name', 'rating', 'scheduled_at')
    list_filter = ('rating', 'scheduled_at')
    search_fields = (
        'interviewer_name',
        'notes',
        'application__candidate__full_name',
        'application__candidate__email',
        'application__job_posting__title',
    )
    list_select_related = (
        'application',
        'application__candidate',
        'application__job_posting',
    )
