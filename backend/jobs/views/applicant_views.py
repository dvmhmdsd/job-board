from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import User, Applicant, Experience, JobApplication
from ..auth import require_authentication, require_ownership_or_admin, require_role


class ApplicantListView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get all applicants (authentication required)",
        operation_summary="List Applicants",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT token in format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="List of applicants",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'applicants': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'user_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'user_email': openapi.Schema(type=openapi.TYPE_STRING),
                                    'linkedin': openapi.Schema(type=openapi.TYPE_STRING),
                                    'github': openapi.Schema(type=openapi.TYPE_STRING),
                                    'resume': openapi.Schema(type=openapi.TYPE_STRING),
                                    'skills': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            401: openapi.Response(description="Authentication required")
        },
        tags=['Applicants']
    )
    @require_authentication
    def get(self, request):
        """Get all applicants - Authenticated users only"""
        applicants = Applicant.objects.select_related('user').all()
        applicants_data = []
        for applicant in applicants:
            applicants_data.append({
                'id': applicant.id,
                'user_id': applicant.user.id,
                'user_name': applicant.user.name,
                'user_email': applicant.user.email,
                'linkedin': applicant.linkedin,
                'github': applicant.github,
                'resume': applicant.resume,
                'skills': applicant.skills
            })
        return Response({'applicants': applicants_data})


class ApplicantDetailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Get specific applicant details with experiences and applications (owner only)",
        operation_summary="Get Applicant Details",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT token in format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Applicant details with experiences and applications",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'user_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'user_email': openapi.Schema(type=openapi.TYPE_STRING),
                        'linkedin': openapi.Schema(type=openapi.TYPE_STRING),
                        'github': openapi.Schema(type=openapi.TYPE_STRING),
                        'resume': openapi.Schema(type=openapi.TYPE_STRING),
                        'skills': openapi.Schema(type=openapi.TYPE_STRING),
                        'experiences': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'applications': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    }
                )
            ),
            401: openapi.Response(description="Authentication required"),
            403: openapi.Response(description="Access denied - owner only"),
            404: openapi.Response(description="Applicant not found")
        },
        tags=['Applicants']
    )
    @require_ownership_or_admin('applicant', 'applicant_id')
    def get(self, request, applicant_id):
        """Get a specific applicant - Owner only"""
        applicant = get_object_or_404(Applicant, id=applicant_id)
        
        # Get all experiences for this applicant
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
        
        # Get all applications for this applicant
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
        
        return Response({
            'id': applicant.id,
            'user_id': applicant.user.id,
            'user_name': applicant.user.name,
            'user_email': applicant.user.email,
            'linkedin': applicant.linkedin,
            'github': applicant.github,
            'resume': applicant.resume,
            'skills': applicant.skills,
            'experiences': experiences_data,
            'applications': applications_data
        })
    
    @swagger_auto_schema(
        operation_description="Update a specific applicant (owner only)",
        operation_summary="Update Applicant",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT token in format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'linkedin': openapi.Schema(type=openapi.TYPE_STRING),
                'github': openapi.Schema(type=openapi.TYPE_STRING),
                'resume': openapi.Schema(type=openapi.TYPE_STRING),
                'skills': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description="Applicant updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'linkedin': openapi.Schema(type=openapi.TYPE_STRING),
                        'github': openapi.Schema(type=openapi.TYPE_STRING),
                        'resume': openapi.Schema(type=openapi.TYPE_STRING),
                        'skills': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Invalid input"),
            401: openapi.Response(description="Authentication required"),
            403: openapi.Response(description="Access denied - owner only"),
            404: openapi.Response(description="Applicant not found")
        },
        tags=['Applicants']
    )
    @require_ownership_or_admin('applicant', 'applicant_id')
    def put(self, request, applicant_id):
        """Update a specific applicant - Owner only"""
        try:
            applicant = get_object_or_404(Applicant, id=applicant_id)
            data = request.data
            
            applicant.linkedin = data.get('linkedin', applicant.linkedin)
            applicant.github = data.get('github', applicant.github)
            applicant.resume = data.get('resume', applicant.resume)
            applicant.skills = data.get('skills', applicant.skills)
            applicant.save()
            
            return Response({
                'id': applicant.id,
                'user_id': applicant.user.id,
                'linkedin': applicant.linkedin,
                'github': applicant.github,
                'resume': applicant.resume,
                'skills': applicant.skills
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Delete a specific applicant (owner only)",
        operation_summary="Delete Applicant",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT token in format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: openapi.Response(description="Applicant deleted successfully"),
            401: openapi.Response(description="Authentication required"),
            403: openapi.Response(description="Access denied - owner only"),
            404: openapi.Response(description="Applicant not found")
        },
        tags=['Applicants']
    )
    @require_ownership_or_admin('applicant', 'applicant_id')
    def delete(self, request, applicant_id):
        """Delete a specific applicant - Owner only"""
        applicant = get_object_or_404(Applicant, id=applicant_id)
        applicant.delete()
        return Response({'message': 'Applicant deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
