from django.urls import path
from . import views
from .views import job_search_views

urlpatterns = [
    # Index endpoint
    path('', views.index, name='index'),
    
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),
    
    # User endpoints
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Applicant endpoints
    path('applicants/', views.ApplicantListView.as_view(), name='applicant-list'),
    path('applicants/<int:applicant_id>/', views.ApplicantDetailView.as_view(), name='applicant-detail'),
    
    # Company endpoints
    path('companies/', views.CompanyListView.as_view(), name='company-list'),
    path('companies/<int:company_id>/', views.CompanyDetailView.as_view(), name='company-detail'),
    
    # Job endpoints
    path('jobs/', views.JobListView.as_view(), name='job-list'),
    path('jobs/<int:job_id>/', views.JobDetailView.as_view(), name='job-detail'),
    path('jobs/search/', job_search_views.search_jobs, name='job-search'),
    
    # Experience endpoints
    path('experiences/<int:applicant_id>/', views.ExperienceListView.as_view(), name='experience-list'),
    
    # Job Application endpoints
    path('applications/', views.JobApplicationListView.as_view(), name='application-list'),
    path('applications/<int:application_id>/', views.JobApplicationDetailView.as_view(), name='application-detail'),
    
    # Additional utility endpoints
    path('companies/<int:company_id>/jobs/', views.JobsByCompanyView.as_view(), name='jobs-by-company'),
    path('applicants/<int:applicant_id>/applications/', views.ApplicationsByApplicantView.as_view(), name='applications-by-applicant'),
    path('applicants/<int:applicant_id>/experiences/', views.ExperiencesByApplicantView.as_view(), name='experiences-by-applicant'),
]