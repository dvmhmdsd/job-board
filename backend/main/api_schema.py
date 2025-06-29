"""
Manual API Schema for Job Portal API

Since we're using Django views instead of DRF APIView,
we need to manually define the schema for Swagger documentation.
"""

from drf_yasg import openapi

# Manual schema definition for Job Portal API
job_portal_schema = openapi.Info(
    title="Job Portal API",
    default_version='v1',
    description="""
    # Job Portal API Documentation
    
    A comprehensive REST API for a Job Portal application with authentication and role-based access control.
    
    ## Features
    - **User Management**: Registration, login, and profile management
    - **Role-based Access**: Applicant and Company roles
    - **Job Management**: CRUD operations for job postings
    - **Application Tracking**: Job application management
    - **Experience Management**: Work experience tracking
    - **JWT Authentication**: Secure token-based authentication
    
    ## Authentication
    This API uses JWT (JSON Web Token) authentication. To access protected endpoints:
    
    1. Register or login to get a JWT token
    2. Include the token in the Authorization header: `Bearer <your-token>`
    
    ## Roles
    - **Applicant**: Can view jobs, apply for jobs, manage their profile and experiences
    - **Company**: Can post jobs, manage company profile, view applications
    
    """,
)
