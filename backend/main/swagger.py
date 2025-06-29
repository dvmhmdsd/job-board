from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .api_schema import job_portal_schema

# Swagger schema configuration
schema_view = get_schema_view(
    job_portal_schema,
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)
