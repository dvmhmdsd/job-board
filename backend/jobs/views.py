# Central import hub for all view modules
# This file imports all views from the separated modules to maintain
# backward compatibility with existing URL patterns and imports

from django.http import HttpResponse

# Import all views from separated modules
from .views.user_views import UserListView, UserDetailView
from .views.applicant_views import ApplicantListView, ApplicantDetailView
from .views.company_views import CompanyListView, CompanyDetailView
from .views.job_views import JobListView, JobDetailView
from .views.experience_views import ExperienceListView
from .views.job_application_views import JobApplicationListView, JobApplicationDetailView
from .views.utility_views import jobs_by_company, applications_by_applicant, experiences_by_applicant
from .views.auth_views import RegisterView, LoginView, ProfileView

def index(request):
    """Main API index endpoint"""
    return HttpResponse("Job Portal API - Available endpoints for Users, Applicants, Companies, Jobs, Experiences, and JobApplications")

# Make all views available when importing from jobs.views
__all__ = [
    'index',
    'UserListView',
    'UserDetailView', 
    'ApplicantListView',
    'ApplicantDetailView',
    'CompanyListView',
    'CompanyDetailView',
    'JobListView',
    'JobDetailView',
    'ExperienceListView',
    'JobApplicationListView',
    'JobApplicationDetailView',
    'jobs_by_company',
    'applications_by_applicant',
    'experiences_by_applicant',
    'RegisterView',
    'LoginView',
    'ProfileView',
]