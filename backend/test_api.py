#!/usr/bin/env python3
"""
Job Portal API Test Script

This script demonstrates how to use the Job Portal API endpoints
with authentication and CRUD operations.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api():
    print("=== Job Portal API Test ===\n")
    
    # Test API info endpoint
    print("1. Testing API Info endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}\n")
    
    # Test user registration
    print("2. Testing User Registration...")
    registration_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "role": "applicant",
        "name": "Test User",
        "linkedin": "https://linkedin.com/in/testuser",
        "skills": "Python, Django, React"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", 
                           json=registration_data,
                           headers={'Content-Type': 'application/json'})
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        token = response.json().get('token')
        print(f"Registration successful! Token: {token[:20]}...")
    else:
        print(f"Registration response: {response.json()}")
    print()
    
    # Test login
    print("3. Testing User Login...")
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", 
                           json=login_data,
                           headers={'Content-Type': 'application/json'})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"Login successful! Token: {token[:20]}...")
        
        # Test authenticated endpoint
        print("\n4. Testing Authenticated Profile endpoint...")
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Profile: {response.json()}")
        else:
            print(f"Profile error: {response.json()}")
            
    else:
        print(f"Login failed: {response.json()}")
    print()
    
    # Test public endpoints
    print("5. Testing Public Endpoints...")
    
    # Test jobs endpoint
    response = requests.get(f"{BASE_URL}/jobs/")
    print(f"Jobs endpoint status: {response.status_code}")
    
    # Test users endpoint
    response = requests.get(f"{BASE_URL}/users/")
    print(f"Users endpoint status: {response.status_code}")
    
    # Test companies endpoint
    response = requests.get(f"{BASE_URL}/companies/")
    print(f"Companies endpoint status: {response.status_code}")
    
    print("\n=== API Documentation Links ===")
    print("Swagger UI: http://localhost:8000/swagger/")
    print("ReDoc: http://localhost:8000/redoc/")
    print("OpenAPI JSON: http://localhost:8000/swagger.json")
    print("OpenAPI YAML: http://localhost:8000/swagger.yaml")

if __name__ == "__main__":
    test_api()
