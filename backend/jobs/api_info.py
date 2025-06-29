from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_description="Get API information and available endpoints",
    operation_summary="API Info",
    responses={
        200: openapi.Response(
            description="API information",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'version': openapi.Schema(type=openapi.TYPE_STRING),
                    'endpoints': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'authentication': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            'users': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            'applicants': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            'companies': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            'jobs': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            'applications': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            'experiences': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                        }
                    )
                }
            )
        )
    },
    tags=['API Info']
)
@csrf_exempt
def api_info(request):
    """Get API information and available endpoints"""
    return JsonResponse({
        'message': 'Job Portal API - A comprehensive REST API for job portal functionality',
        'version': 'v1.0',
        'documentation': {
            'swagger': '/swagger/',
            'redoc': '/redoc/',
            'openapi_json': '/swagger.json',
            'openapi_yaml': '/swagger.yaml'
        },
        'endpoints': {
            'authentication': [
                'POST /api/auth/register/ - Register new user',
                'POST /api/auth/login/ - Login user',
                'GET /api/auth/profile/ - Get user profile'
            ],
            'users': [
                'GET /api/users/ - List all users',
                'GET /api/users/<id>/ - Get user details',
                'PUT /api/users/<id>/ - Update user',
                'DELETE /api/users/<id>/ - Delete user'
            ],
            'applicants': [
                'GET /api/applicants/ - List all applicants',
                'GET /api/applicants/<id>/ - Get applicant details',
                'PUT /api/applicants/<id>/ - Update applicant',
                'DELETE /api/applicants/<id>/ - Delete applicant'
            ],
            'companies': [
                'GET /api/companies/ - List all companies',
                'GET /api/companies/<id>/ - Get company details',
                'PUT /api/companies/<id>/ - Update company',
                'DELETE /api/companies/<id>/ - Delete company'
            ],
            'jobs': [
                'GET /api/jobs/ - List all jobs',
                'POST /api/jobs/ - Create new job',
                'GET /api/jobs/<id>/ - Get job details',
                'PUT /api/jobs/<id>/ - Update job',
                'DELETE /api/jobs/<id>/ - Delete job'
            ],
            'applications': [
                'GET /api/applications/ - List all applications',
                'POST /api/applications/ - Create new application',
                'GET /api/applications/<id>/ - Get application details',
                'PUT /api/applications/<id>/ - Update application',
                'DELETE /api/applications/<id>/ - Delete application'
            ],
            'experiences': [
                'GET /api/experiences/ - List all experiences',
                'POST /api/experiences/ - Create new experience',
                'GET /api/experiences/<id>/ - Get experience details',
                'PUT /api/experiences/<id>/ - Update experience',
                'DELETE /api/experiences/<id>/ - Delete experience'
            ]
        }
    })
