from rest_framework import serializers
from .models import Job, Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['name', 'logo', 'website']

class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 
            'title', 
            'description', 
            'location', 
            'salary', 
            'job_type', 
            'skills', 
            'company',
            'application_url',
            'created_at'
        ]
