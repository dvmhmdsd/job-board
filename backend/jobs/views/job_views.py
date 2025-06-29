from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import json
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import Company, Job
from ..auth import require_role, require_ownership_or_admin


class JobListView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get all job listings",
        operation_summary="List Jobs",
        responses={
            200: openapi.Response(
                description="List of jobs",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'jobs': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'company_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'company_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                    'location': openapi.Schema(type=openapi.TYPE_STRING),
                                    'application_url': openapi.Schema(type=openapi.TYPE_STRING),
                                    'salary': openapi.Schema(type=openapi.TYPE_STRING),
                                    'skills': openapi.Schema(type=openapi.TYPE_STRING),
                                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                                    'job_type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                }
                            )
                        )
                    }
                )
            )
        },
        tags=['Jobs']
    )
    def get(self, request):
        """Get all jobs"""
        jobs = Job.objects.select_related('company').all()
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'company_id': job.company.id,
                'company_name': job.company.name,
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
    
    @swagger_auto_schema(
        operation_description="Create a new job posting (requires company role)",
        operation_summary="Create Job",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['company_id', 'title', 'description', 'location', 'application_url', 'salary', 'skills', 'status', 'job_type'],
            properties={
                'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Company ID'),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Job title'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Job description'),
                'location': openapi.Schema(type=openapi.TYPE_STRING, description='Job location'),
                'application_url': openapi.Schema(type=openapi.TYPE_STRING, description='Application URL'),
                'salary': openapi.Schema(type=openapi.TYPE_NUMBER, description='Salary amount'),
                'skills': openapi.Schema(type=openapi.TYPE_STRING, description='Required skills'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Job status'),
                'job_type': openapi.Schema(type=openapi.TYPE_STRING, description='Job type'),
            }
        ),
        responses={
            201: openapi.Response(description="Job created successfully"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Authentication required"),
            403: openapi.Response(description="Company role required")
        },
        tags=['Jobs']
    )
    @require_role('company')
    def post(self, request):
        """Create a new job"""
        try:
            data = request.data
            company = get_object_or_404(Company, id=data['company_id'])
            
            job = Job.objects.create(
                company=company,
                title=data['title'],
                description=data['description'],
                location=data['location'],
                application_url=data['application_url'],
                salary=Decimal(str(data['salary'])),
                skills=data['skills'],
                status=data['status'],
                job_type=data['job_type']
            )
            return Response({
                'id': job.id,
                'company_id': job.company.id,
                'title': job.title,
                'description': job.description,
                'location': job.location,
                'application_url': job.application_url,
                'salary': str(job.salary),
                'skills': job.skills,
                'status': job.status,
                'job_type': job.job_type,
                'created_at': job.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class JobDetailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific job by ID",
        operation_summary="Get Job",
        manual_parameters=[
            openapi.Parameter(
                'job_id',
                openapi.IN_PATH,
                description="ID of the job to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Job details",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'company_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'company_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'description': openapi.Schema(type=openapi.TYPE_STRING),
                        'location': openapi.Schema(type=openapi.TYPE_STRING),
                        'application_url': openapi.Schema(type=openapi.TYPE_STRING),
                        'salary': openapi.Schema(type=openapi.TYPE_STRING),
                        'skills': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'job_type': openapi.Schema(type=openapi.TYPE_STRING),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    }
                )
            ),
            404: openapi.Response(description="Job not found")
        },
        tags=['Jobs']
    )
    def get(self, request, job_id):
        """Get a specific job"""
        job = get_object_or_404(Job, id=job_id)
        return Response({
            'id': job.id,
            'company_id': job.company.id,
            'company_name': job.company.name,
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

    @swagger_auto_schema(
        operation_description="Update a specific job by ID (requires ownership or admin)",
        operation_summary="Update Job",
        manual_parameters=[
            openapi.Parameter(
                'job_id',
                openapi.IN_PATH,
                description="ID of the job to update",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Job title'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Job description'),
                'location': openapi.Schema(type=openapi.TYPE_STRING, description='Job location'),
                'application_url': openapi.Schema(type=openapi.TYPE_STRING, description='Application URL'),
                'salary': openapi.Schema(type=openapi.TYPE_NUMBER, description='Salary amount'),
                'skills': openapi.Schema(type=openapi.TYPE_STRING, description='Required skills'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Job status'),
                'job_type': openapi.Schema(type=openapi.TYPE_STRING, description='Job type'),
            }
        ),
        responses={
            200: openapi.Response(description="Job updated successfully"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Authentication required"),
            403: openapi.Response(description="Ownership or admin required"),
            404: openapi.Response(description="Job not found")
        },
        tags=['Jobs']
    )
    @require_ownership_or_admin('job', 'company')
    def put(self, request, job_id):
        """Update a specific job"""
        try:
            job = get_object_or_404(Job, id=job_id)
            data = request.data
            
            job.title = data.get('title', job.title)
            job.description = data.get('description', job.description)
            job.location = data.get('location', job.location)
            job.application_url = data.get('application_url', job.application_url)
            if 'salary' in data:
                job.salary = Decimal(str(data['salary']))
            job.skills = data.get('skills', job.skills)
            job.status = data.get('status', job.status)
            job.job_type = data.get('job_type', job.job_type)
            job.save()
            
            return Response({
                'id': job.id,
                'company_id': job.company.id,
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
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Delete a specific job by ID (requires ownership or admin)",
        operation_summary="Delete Job",
        manual_parameters=[
            openapi.Parameter(
                'job_id',
                openapi.IN_PATH,
                description="ID of the job to delete",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: openapi.Response(description="Job deleted successfully"),
            401: openapi.Response(description="Authentication required"),
            403: openapi.Response(description="Ownership or admin required"),
            404: openapi.Response(description="Job not found")
        },
        tags=['Jobs']
    )
    @require_ownership_or_admin('job', 'company')
    def delete(self, request, job_id):
        """Delete a specific job"""
        job = get_object_or_404(Job, id=job_id)
        job.delete()
        return Response({'message': 'Job deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
