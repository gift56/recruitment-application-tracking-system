from django.urls import path

from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.RecruiterLoginView.as_view(), name='login'),
    path(
        'recruiter/',
        views.RecruiterDashboardView.as_view(),
        name='recruiter_dashboard',
    ),
    path(
        'recruiter/jobs/create/',
        views.JobPostingCreateView.as_view(),
        name='recruiter_job_create',
    ),
    path(
        'recruiter/jobs/',
        views.RecruiterJobListView.as_view(),
        name='recruiter_jobs',
    ),
    path(
        'recruiter/jobs/<int:pk>/edit/',
        views.JobPostingUpdateView.as_view(),
        name='recruiter_job_edit',
    ),
    path(
        'recruiter/jobs/<int:pk>/delete/',
        views.JobPostingDeleteView.as_view(),
        name='recruiter_job_delete',
    ),
    path(
        'recruiter/departments/create/',
        views.DepartmentCreateView.as_view(),
        name='recruiter_department_create',
    ),
    path(
        'recruiter/applications/',
        views.RecruiterApplicationListView.as_view(),
        name='recruiter_applications',
    ),
    path(
        'recruiter/applications/<int:pk>/status/',
        views.ApplicationStatusUpdateView.as_view(),
        name='recruiter_application_status',
    ),
    path(
        'recruiter/applications/<int:pk>/notes/',
        views.InterviewNoteCreateView.as_view(),
        name='recruiter_application_note',
    ),
    path(
        'recruiter/applications/<int:pk>/resume/',
        views.ApplicationResumeView.as_view(),
        name='recruiter_application_resume',
    ),
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path(
        'jobs/<int:pk>/apply/',
        views.ApplicationCreateView.as_view(),
        name='application_create',
    ),
]
