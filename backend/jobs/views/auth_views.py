from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import User, Applicant, Company
from ..auth import hash_password, verify_password, generate_jwt_token, require_authentication


class RegisterView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Register a new user account",
        operation_summary="User Registration",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'role', 'name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email address'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['applicant', 'company'], description='User role'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='User full name'),
                'linkedin': openapi.Schema(type=openapi.TYPE_STRING, description='LinkedIn profile URL (applicants only)'),
                'github': openapi.Schema(type=openapi.TYPE_STRING, description='GitHub profile URL (applicants only)'),
                'resume': openapi.Schema(type=openapi.TYPE_STRING, description='Resume URL (applicants only)'),
                'skills': openapi.Schema(type=openapi.TYPE_STRING, description='Skills description (applicants only)'),
                'company_name': openapi.Schema(type=openapi.TYPE_STRING, description='Company name (companies only)'),
                'industry': openapi.Schema(type=openapi.TYPE_STRING, description='Industry (companies only)'),
                'brief': openapi.Schema(type=openapi.TYPE_STRING, description='Company description (companies only)'),
                'website': openapi.Schema(type=openapi.TYPE_STRING, description='Company website (companies only)'),
                'logo': openapi.Schema(type=openapi.TYPE_STRING, description='Company logo URL (companies only)'),
            }
        ),
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT authentication token'),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'role': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description="Bad request - validation errors")
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Register a new user"""
        try:
            data = request.data
            
            # Validate required fields
            required_fields = ['email', 'password', 'role', 'name']
            for field in required_fields:
                if field not in data:
                    return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already exists
            if User.objects.filter(email=data['email']).exists():
                return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate role
            if data['role'] not in ['applicant', 'company']:
                return Response({'error': 'Role must be either "applicant" or "company"'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create user
            user = User.objects.create(
                email=data['email'],
                password_hash=hash_password(data['password']),
                role=data['role'],
                name=data['name']
            )
            
            # Create role-specific profile
            if data['role'] == 'applicant':
                Applicant.objects.create(
                    user=user,
                    linkedin=data.get('linkedin', ''),
                    github=data.get('github', ''),
                    resume=data.get('resume', ''),
                    skills=data.get('skills', '')
                )
            elif data['role'] == 'company':
                # For company registration, require additional fields
                company_required = ['industry', 'brief', 'website']
                for field in company_required:
                    if field not in data:
                        user.delete()  # Cleanup user if company creation fails
                        return Response({'error': f'{field} is required for company registration'}, status=status.HTTP_400_BAD_REQUEST)
                
                Company.objects.create(
                    user=user,
                    name=data.get('company_name', data['name']),
                    industry=data['industry'],
                    logo=data.get('logo', ''),
                    brief=data['brief'],
                    website=data['website']
                )
            
            # Generate token
            token = generate_jwt_token(user)
            
            return Response({
                'message': 'User registered successfully',
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'name': user.name
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Login with email and password to get JWT token",
        operation_summary="User Login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email address'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT authentication token'),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'role': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            ),
            401: openapi.Response(description="Invalid credentials"),
            400: openapi.Response(description="Bad request")
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Login user"""
        try:
            data = request.data
            
            # Validate required fields
            if 'email' not in data or 'password' not in data:
                return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Find user
            try:
                user = User.objects.get(email=data['email'])
            except User.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Verify password
            if not verify_password(data['password'], user.password_hash):
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate token
            token = generate_jwt_token(user)
            
            # Get role-specific data
            profile_data = {}
            if user.role == 'applicant':
                try:
                    applicant = Applicant.objects.get(user=user)
                    profile_data = {
                        'applicant_id': applicant.id,
                        'linkedin': applicant.linkedin,
                        'github': applicant.github,
                        'resume': applicant.resume,
                        'skills': applicant.skills
                    }
                except Applicant.DoesNotExist:
                    pass
            elif user.role == 'company':
                try:
                    company = Company.objects.get(user=user)
                    profile_data = {
                        'company_id': company.id,
                        'company_name': company.name,
                        'industry': company.industry,
                        'logo': company.logo,
                        'brief': company.brief,
                        'website': company.website
                    }
                except Company.DoesNotExist:
                    pass
            
            return Response({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'name': user.name,
                    **profile_data
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [AllowAny]  # We'll handle auth manually with our JWT decorator
    @swagger_auto_schema(
        operation_description="Get current user profile information",
        operation_summary="Get User Profile",
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
                description="User profile data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'role': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'applicant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Only for applicants'),
                                'linkedin': openapi.Schema(type=openapi.TYPE_STRING, description='Only for applicants'),
                                'github': openapi.Schema(type=openapi.TYPE_STRING, description='Only for applicants'),
                                'resume': openapi.Schema(type=openapi.TYPE_STRING, description='Only for applicants'),
                                'skills': openapi.Schema(type=openapi.TYPE_STRING, description='Only for applicants'),
                                'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Only for companies'),
                                'company_name': openapi.Schema(type=openapi.TYPE_STRING, description='Only for companies'),
                                'industry': openapi.Schema(type=openapi.TYPE_STRING, description='Only for companies'),
                                'logo': openapi.Schema(type=openapi.TYPE_STRING, description='Only for companies'),
                                'brief': openapi.Schema(type=openapi.TYPE_STRING, description='Only for companies'),
                                'website': openapi.Schema(type=openapi.TYPE_STRING, description='Only for companies'),
                            }
                        )
                    }
                )
            ),
            401: openapi.Response(description="Authentication required")
        },
        tags=['Authentication']
    )
    @require_authentication
    def get(self, request):
        """Get current user profile"""
        # ...existing code...
        user = request.user
        
        # Get role-specific data
        profile_data = {}
        if user.role == 'applicant':
            try:
                applicant = Applicant.objects.get(user=user)
                profile_data = {
                    'applicant_id': applicant.id,
                    'linkedin': applicant.linkedin,
                    'github': applicant.github,
                    'resume': applicant.resume,
                    'skills': applicant.skills
                }
            except Applicant.DoesNotExist:
                pass
        elif user.role == 'company':
            try:
                company = Company.objects.get(user=user)
                profile_data = {
                    'company_id': company.id,
                    'company_name': company.name,
                    'industry': company.industry,
                    'logo': company.logo,
                    'brief': company.brief,
                    'website': company.website
                }
            except Company.DoesNotExist:
                pass
        
        return JsonResponse({
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'name': user.name,
                **profile_data
            }
        })
