from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime
from ..models import Applicant, Experience
from ..auth import require_authentication


class ExperienceListView(APIView):
    @swagger_auto_schema(
        operation_summary="Get experiences for an applicant",
        operation_description="Retrieve a list of experiences for a specific applicant (requires authentication).",
        manual_parameters=[
            openapi.Parameter(
                'applicant_id',
                openapi.IN_QUERY,
                description="ID of the applicant",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="List of experiences for the applicant",
                examples={
                    "application/json": {
                        "experiences": [
                            {
                                "id": 1,
                                "applicant_id": 1,
                                "applicant_name": "John Doe",
                                "company_name": "Tech Corp",
                                "job_title": "Software Developer",
                                "start_date": "2022-01-01",
                                "end_date": "2023-12-31",
                                "description": "Developed web applications",
                                "skills": "Python, Django, React"
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
            404: openapi.Response(description="Applicant not found")
        },
        tags=["Experiences"]
    )
    @require_authentication
    def get(self, request):
        """Get experiences for a specific applicant"""
        applicant_id = request.query_params.get('applicant_id')
        if not applicant_id:
            return Response({'error': 'applicant_id query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            applicant = get_object_or_404(Applicant, id=applicant_id)
            experiences = Experience.objects.filter(applicant=applicant).select_related('applicant__user')
            experiences_data = []
            for exp in experiences:
                experiences_data.append({
                    'id': exp.id,
                    'applicant_id': exp.applicant.id,
                    'applicant_name': exp.applicant.user.name,
                    'company_name': exp.company_name,
                    'job_title': exp.job_title,
                    'start_date': exp.start_date.isoformat(),
                    'end_date': exp.end_date.isoformat() if exp.end_date else None,
                    'description': exp.description,
                    'skills': exp.skills
                })
            return Response({'experiences': experiences_data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Create a new experience",
        operation_description="Create a new work experience entry.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['company_name', 'job_title', 'start_date', 'description', 'skills'],
            properties={
                'company_name': openapi.Schema(type=openapi.TYPE_STRING, description='Company name'),
                'job_title': openapi.Schema(type=openapi.TYPE_STRING, description='Job title'),
                'start_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Start date (YYYY-MM-DD)'),
                'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='End date (YYYY-MM-DD)', x_nullable=True),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Job description'),
                'skills': openapi.Schema(type=openapi.TYPE_STRING, description='Skills used'),
            }
        ),
        manual_parameters=[
            openapi.Parameter(
                'applicant_id',
                openapi.IN_QUERY,
                description="ID of the applicant",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            201: openapi.Response(description="Experience created successfully"),
            400: openapi.Response(description="Bad request"),
            404: openapi.Response(description="Applicant not found")
        },
        tags=["Experiences"]
    )
    def post(self, request):
        """Create a new experience"""
        try:
            applicant_id = request.query_params.get('applicant_id')
            if not applicant_id:
                return Response({'error': 'applicant_id query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
            applicant = get_object_or_404(Applicant, id=applicant_id)
            data = request.data
            
            experience = Experience.objects.create(
                applicant=applicant,
                company_name=data['company_name'],
                job_title=data['job_title'],
                start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
                description=data['description'],
                skills=data['skills']
            )
            return Response({
                'id': experience.id,
                'applicant_id': experience.applicant.id,
                'company_name': experience.company_name,
                'job_title': experience.job_title,
                'start_date': experience.start_date.isoformat(),
                'end_date': experience.end_date.isoformat() if experience.end_date else None,
                'description': experience.description,
                'skills': experience.skills
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
