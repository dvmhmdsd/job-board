from .user_views import UserListView, UserDetailView
from .applicant_views import ApplicantListView, ApplicantDetailView
from .company_views import CompanyListView, CompanyDetailView
from .job_views import JobListView, JobDetailView
from .experience_views import ExperienceListView
from .job_application_views import JobApplicationListView, JobApplicationDetailView
from .utility_views import JobsByCompanyView, ApplicationsByApplicantView, ExperiencesByApplicantView
from .auth_views import RegisterView, LoginView, ProfileView
from . import job_search_views

def index(request):
    from django.http import HttpResponse
    return HttpResponse("Job Portal API - Available endpoints for Users, Applicants, Companies, Jobs, Experiences, and JobApplications")

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
    'JobsByCompanyView',
    'ApplicationsByApplicantView',
    'ExperiencesByApplicantView',
    'RegisterView',
    'LoginView',
    'ProfileView',
    'job_search_views',
]
