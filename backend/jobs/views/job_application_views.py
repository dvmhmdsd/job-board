from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import Applicant, Job, JobApplication
from ..auth import require_authentication, require_ownership_or_admin, require_role


class JobApplicationListView(APIView):
    @swagger_auto_schema(
        operation_summary="Get all job applications",
        operation_description="Retrieve a list of all job applications (requires authentication).",
        responses={
            200: openapi.Response(
                description="List of job applications",
                examples={
                    "application/json": {
                        "applications": [
                            {
                                "id": 1,
                                "applicant_id": 1,
                                "applicant_name": "John Doe",
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
            401: openapi.Response(description="Unauthorized")
        },
        tags=["Job Applications"]
    )
    @require_authentication
    def get(self, request):
        """Get all job applications"""
        applications = JobApplication.objects.select_related('applicant__user', 'job__company').all()
        applications_data = []
        for app in applications:
            applications_data.append({
                'id': app.id,
                'applicant_id': app.applicant.id,
                'applicant_name': app.applicant.user.name,
                'job_id': app.job.id,
                'job_title': app.job_title,
                'company_name': app.company_name,
                'job_url': app.job_url,
                'status': app.status,
                'applied_at': app.applied_at.isoformat()
            })
        return Response({'applications': applications_data})
    
    @swagger_auto_schema(
        operation_summary="Create a new job application",
        operation_description="Create a new job application (requires applicant role).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['applicant_id', 'job_id', 'company_name', 'status', 'job_title', 'job_url'],
            properties={
                'applicant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Applicant ID'),
                'job_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Job ID'),
                'company_name': openapi.Schema(type=openapi.TYPE_STRING, description='Company name'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Application status'),
                'job_title': openapi.Schema(type=openapi.TYPE_STRING, description='Job title'),
                'job_url': openapi.Schema(type=openapi.TYPE_STRING, description='Job URL'),
            }
        ),
        responses={
            201: openapi.Response(description="Job application created successfully"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - requires applicant role"),
            404: openapi.Response(description="Applicant or Job not found")
        },
        tags=["Job Applications"]
    )
    @require_role('applicant')
    def post(self, request):
        """Create a new job application"""
        try:
            data = request.data
            applicant = get_object_or_404(Applicant, id=data['applicant_id'])
            job = get_object_or_404(Job, id=data['job_id'])
            
            application = JobApplication.objects.create(
                applicant=applicant,
                job=job,
                company_name=data['company_name'],
                status=data['status'],
                job_title=data['job_title'],
                job_url=data['job_url']
            )
            return Response({
                'id': application.id,
                'applicant_id': application.applicant.id,
                'job_id': application.job.id,
                'company_name': application.company_name,
                'status': application.status,
                'job_title': application.job_title,
                'job_url': application.job_url,
                'applied_at': application.applied_at.isoformat()
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class JobApplicationDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="Get a specific job application",
        operation_description="Retrieve details of a job application by ID (requires authentication).",
        responses={
            200: openapi.Response(
                description="Job application details",
                examples={
                    "application/json": {
                        "id": 1,
                        "applicant_id": 1,
                        "applicant_name": "John Doe",
                        "job_id": 1,
                        "job_title": "Software Engineer",
                        "company_name": "Tech Corp",
                        "job_url": "http://techcorp.com/jobs/1",
                        "status": "applied",
                        "applied_at": "2024-01-15T10:30:00Z"
                    }
                }
            ),
            401: openapi.Response(description="Unauthorized"),
            404: openapi.Response(description="Job application not found")
        },
        tags=["Job Applications"]
    )
    @require_authentication
    def get(self, request, application_id):
        """Get a specific job application"""
        app = get_object_or_404(JobApplication, id=application_id)
        return Response({
            'id': app.id,
            'applicant_id': app.applicant.id,
            'applicant_name': app.applicant.user.name,
            'job_id': app.job.id,
            'job_title': app.job_title,
            'company_name': app.company_name,
            'job_url': app.job_url,
            'status': app.status,
            'applied_at': app.applied_at.isoformat()
        })
    
    @swagger_auto_schema(
        operation_summary="Update a specific job application",
        operation_description="Update job application details. Only the applicant who owns the application or admin can update.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'company_name': openapi.Schema(type=openapi.TYPE_STRING, description='Company name'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Application status'),
                'job_title': openapi.Schema(type=openapi.TYPE_STRING, description='Job title'),
                'job_url': openapi.Schema(type=openapi.TYPE_STRING, description='Job URL'),
            }
        ),
        responses={
            200: openapi.Response(description="Job application updated successfully"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Job application not found")
        },
        tags=["Job Applications"]
    )
    @require_ownership_or_admin('jobapplication', 'applicant')
    def put(self, request, application_id):
        """Update a specific job application"""
        try:
            app = get_object_or_404(JobApplication, id=application_id)
            data = request.data
            
            app.company_name = data.get('company_name', app.company_name)
            app.status = data.get('status', app.status)
            app.job_title = data.get('job_title', app.job_title)
            app.job_url = data.get('job_url', app.job_url)
            app.save()
            
            return Response({
                'id': app.id,
                'applicant_id': app.applicant.id,
                'job_id': app.job.id,
                'company_name': app.company_name,
                'status': app.status,
                'job_title': app.job_title,
                'job_url': app.job_url,
                'applied_at': app.applied_at.isoformat()
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Delete a specific job application",
        operation_description="Delete a job application. Only the applicant who owns the application or admin can delete.",
        responses={
            204: openapi.Response(description="Job application deleted successfully"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Job application not found")
        },
        tags=["Job Applications"]
    )
    @require_ownership_or_admin('jobapplication', 'applicant')
    def delete(self, request, application_id):
        """Delete a specific job application"""
        app = get_object_or_404(JobApplication, id=application_id)
        app.delete()
        return Response({'message': 'Job application deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
