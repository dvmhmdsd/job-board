from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import User, Company
from ..auth import require_authentication, require_ownership_or_admin, require_role


class CompanyListView(APIView):
    @swagger_auto_schema(
        operation_summary="Get all companies",
        operation_description="Retrieve a list of all companies in the system.",
        responses={
            200: openapi.Response(
                description="List of companies",
                examples={
                    "application/json": {
                        "companies": [
                            {
                                "id": 1,
                                "user_id": 1,
                                "user_email": "company@example.com",
                                "name": "Tech Corp",
                                "industry": "Technology",
                                "logo": "http://example.com/logo.png",
                                "brief": "A tech company",
                                "website": "http://techcorp.com"
                            }
                        ]
                    }
                }
            )
        },
        tags=["Companies"]
    )
    def get(self, request):
        """Get all companies"""
        companies = Company.objects.select_related('user').all()
        companies_data = []
        for company in companies:
            companies_data.append({
                'id': company.id,
                'user_id': company.user.id,
                'user_email': company.user.email,
                'name': company.name,
                'industry': company.industry,
                'logo': company.logo,
                'brief': company.brief,
                'website': company.website
            })
        return Response({'companies': companies_data})

class CompanyDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="Get a specific company",
        operation_description="Retrieve details of a company by ID.",
        responses={
            200: openapi.Response(
                description="Company details",
                examples={
                    "application/json": {
                        "id": 1,
                        "user_id": 1,
                        "user_email": "company@example.com",
                        "name": "Tech Corp",
                        "industry": "Technology",
                        "logo": "http://example.com/logo.png",
                        "brief": "A tech company",
                        "website": "http://techcorp.com"
                    }
                }
            ),
            404: openapi.Response(description="Company not found")
        },
        tags=["Companies"]
    )
    def get(self, request, company_id):
        """Get a specific company"""
        company = get_object_or_404(Company, id=company_id)
        return Response({
            'id': company.id,
            'user_id': company.user.id,
            'user_email': company.user.email,
            'name': company.name,
            'industry': company.industry,
            'logo': company.logo,
            'brief': company.brief,
            'website': company.website
        })

    @swagger_auto_schema(
        operation_summary="Update a specific company",
        operation_description="Update company details. Only the company owner or admin can update.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Company name'),
                'industry': openapi.Schema(type=openapi.TYPE_STRING, description='Industry'),
                'logo': openapi.Schema(type=openapi.TYPE_STRING, description='Logo URL'),
                'brief': openapi.Schema(type=openapi.TYPE_STRING, description='Company brief'),
                'website': openapi.Schema(type=openapi.TYPE_STRING, description='Website URL'),
            }
        ),
        responses={
            200: openapi.Response(description="Company updated successfully"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Company not found")
        },
        tags=["Companies"]
    )
    @require_ownership_or_admin('company', 'company_id')
    def put(self, request, company_id):
        """Update a specific company"""
        try:
            company = get_object_or_404(Company, id=company_id)
            data = request.data
            
            company.name = data.get('name', company.name)
            company.industry = data.get('industry', company.industry)
            company.logo = data.get('logo', company.logo)
            company.brief = data.get('brief', company.brief)
            company.website = data.get('website', company.website)
            company.save()
            
            return Response({
                'id': company.id,
                'user_id': company.user.id,
                'name': company.name,
                'industry': company.industry,
                'logo': company.logo,
                'brief': company.brief,
                'website': company.website
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Delete a specific company",
        operation_description="Delete a company. Only the company owner or admin can delete.",
        responses={
            204: openapi.Response(description="Company deleted successfully"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Company not found")
        },
        tags=["Companies"]
    )
    @require_ownership_or_admin('company', 'company_id')
    def delete(self, request, company_id):
        """Delete a specific company"""
        company = get_object_or_404(Company, id=company_id)
        company.delete()
        return Response({'message': 'Company deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
