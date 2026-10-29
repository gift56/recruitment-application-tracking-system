from django.urls import path

from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path(
        'jobs/<int:pk>/apply/',
        views.ApplicationCreateView.as_view(),
        name='application_create',
    ),
]
