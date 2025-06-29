from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import Company, Job, Applicant, JobApplication, Experience
from ..auth import require_authentication, require_ownership_or_admin


class JobsByCompanyView(APIView):
    @swagger_auto_schema(
        operation_summary="Get all jobs for a specific company",
        operation_description="Retrieve all jobs posted by a specific company (requires authentication).",
        responses={
            200: openapi.Response(
                description="List of jobs by company",
                examples={
                    "application/json": {
                        "jobs": [
                            {
                                "id": 1,
                                "title": "Software Engineer",
                                "description": "Develop web applications",
                                "location": "New York",
                                "application_url": "http://example.com/apply",
                                "salary": "100000.00",
                                "skills": "Python, Django",
                                "status": "active",
                                "job_type": "full-time",
                                "created_at": "2024-01-15T10:30:00Z"
                            }
                        ]
                    }
                }
            ),
            401: openapi.Response(description="Unauthorized"),
            404: openapi.Response(description="Company not found")
        },
        tags=["Utility"]
    )
    @require_authentication
    def get(self, request, company_id):
        """Get all jobs for a specific company"""
        company = get_object_or_404(Company, id=company_id)
        jobs = Job.objects.filter(company=company)
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'description': job.description,
                'location': job.location,
                'application_url': job.application_url,
                'salary': str(job.salary),
                'skills': job.skills,
                'status': job.status,
                'job_type': job.job_type,
                'created_at': job.created_at.isoformat()
            })
        return Response({'jobs': jobs_data})


class ApplicationsByApplicantView(APIView):
    @swagger_auto_schema(
        operation_summary="Get all applications for a specific applicant",
        operation_description="Retrieve all job applications for a specific applicant. Only the applicant owner or admin can access.",
        responses={
            200: openapi.Response(
                description="List of applications by applicant",
                examples={
                    "application/json": {
                        "applications": [
                            {
                                "id": 1,
                                "job_id": 1,
                                "job_title": "Software Engineer",
                                "company_name": "Tech Corp",
                                "job_url": "http://techcorp.com/jobs/1",
                                "status": "applied",
                                "applied_at": "2024-01-15T10:30:00Z"
                            }
                        ]
                    }
                }
            ),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Applicant not found")
        },
        tags=["Utility"]
    )
    @require_ownership_or_admin('applicant', 'applicant_id')
    def get(self, request, applicant_id):
        """Get all applications for a specific applicant - Owner only"""
        applicant = get_object_or_404(Applicant, id=applicant_id)
        applications = JobApplication.objects.filter(applicant=applicant)
        applications_data = []
        for app in applications:
            applications_data.append({
                'id': app.id,
                'job_id': app.job.id,
                'job_title': app.job_title,
                'company_name': app.company_name,
                'job_url': app.job_url,
                'status': app.status,
                'applied_at': app.applied_at.isoformat()
            })
        return Response({'applications': applications_data})


class ExperiencesByApplicantView(APIView):
    @swagger_auto_schema(
        operation_summary="Get all experiences for a specific applicant",
        operation_description="Retrieve all work experiences for a specific applicant. Only the applicant owner or admin can access.",
        responses={
            200: openapi.Response(
                description="List of experiences by applicant",
                examples={
                    "application/json": {
                        "experiences": [
                            {
                                "id": 1,
                                "company_name": "Previous Corp",
                                "job_title": "Junior Developer",
                                "start_date": "2022-01-01",
                                "end_date": "2023-12-31",
                                "description": "Developed web applications",
                                "skills": "Python, Django"
                            }
                        ]
                    }
                }
            ),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Applicant not found")
        },
        tags=["Utility"]
    )
    @require_ownership_or_admin('applicant', 'applicant_id')
    def get(self, request, applicant_id):
        """Get all experiences for a specific applicant - Owner only"""
        applicant = get_object_or_404(Applicant, id=applicant_id)
        experiences = Experience.objects.filter(applicant=applicant)
        experiences_data = []
        for exp in experiences:
            experiences_data.append({
                'id': exp.id,
                'company_name': exp.company_name,
                'job_title': exp.job_title,
                'start_date': exp.start_date.isoformat(),
                'end_date': exp.end_date.isoformat() if exp.end_date else None,
                'description': exp.description,
                'skills': exp.skills
            })
        return Response({'experiences': experiences_data})
