import jwt
import hashlib
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse
from functools import wraps
from .models import User, Applicant, Company

# JWT Secret Key - In production, this should be in environment variables
JWT_SECRET = getattr(settings, 'JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(days=7)

def hash_password(password):
    """Hash a password for storing in the database"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed_password

def generate_jwt_token(user):
    """Generate JWT token for a user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_from_token(request):
    """Extract user from JWT token in request headers"""
    # Handle both Django and DRF request objects
    if hasattr(request, 'META'):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
    else:
        # For DRF request objects
        auth_header = request.headers.get('Authorization') if hasattr(request, 'headers') else None
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    payload = decode_jwt_token(token)
    if not payload:
        return None
    
    try:
        user = User.objects.get(id=payload['user_id'])
        return user
    except User.DoesNotExist:
        return None

def require_authentication(view_func):
    """Decorator to require authentication for a view"""
    @wraps(view_func)
    def wrapper(view_or_request, *args, **kwargs):
        # Handle both Django views and DRF APIView methods
        if hasattr(view_or_request, 'request'):
            # This is a DRF view instance
            request = view_or_request.request
            view_instance = view_or_request
        else:
            # This is a Django function-based view
            request = view_or_request
            view_instance = None
        
        user = get_user_from_token(request)
        if not user:
            if view_instance:
                # Return DRF Response for APIView
                from rest_framework.response import Response
                from rest_framework import status
                return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # Return Django JsonResponse for function-based views
                from django.http import JsonResponse
                return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Add user to request object for easy access
        request.user = user
        
        if view_instance:
            # Call the method with the view instance
            return view_func(view_instance, *args, **kwargs)
        else:
            # Call the function with the request
            return view_func(request, *args, **kwargs)
    
    return wrapper

def require_role(required_role):
    """Decorator to require specific role for a view"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = get_user_from_token(request)
            if not user:
                # Check if it's a DRF view by looking for Response in the view module
                try:
                    from rest_framework.response import Response
                    return Response({'error': 'Authentication required'}, status=401)
                except ImportError:
                    return JsonResponse({'error': 'Authentication required'}, status=401)
            
            if user.role != required_role:
                try:
                    from rest_framework.response import Response
                    return Response({'error': 'Insufficient permissions'}, status=403)
                except ImportError:
                    return JsonResponse({'error': 'Insufficient permissions'}, status=403)
            
            request.user = user
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def require_ownership_or_admin(model_name, id_param='id'):
    """Decorator to require ownership of a resource or admin role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = get_user_from_token(request)
            if not user:
                try:
                    from rest_framework.response import Response
                    return Response({'error': 'Authentication required'}, status=401)
                except ImportError:
                    return JsonResponse({'error': 'Authentication required'}, status=401)
            
            resource_id = kwargs.get(id_param)
            if not resource_id:
                try:
                    from rest_framework.response import Response
                    return Response({'error': 'Resource ID required'}, status=400)
                except ImportError:
                    return JsonResponse({'error': 'Resource ID required'}, status=400)
            
            # Check ownership based on model type
            try:
                if model_name == 'applicant':
                    applicant = Applicant.objects.get(id=resource_id)
                    if applicant.user.id != user.id:
                        try:
                            from rest_framework.response import Response
                            return Response({'error': 'Access denied'}, status=403)
                        except ImportError:
                            return JsonResponse({'error': 'Access denied'}, status=403)
                elif model_name == 'company':
                    company = Company.objects.get(id=resource_id)
                    if company.user.id != user.id:
                        try:
                            from rest_framework.response import Response
                            return Response({'error': 'Access denied'}, status=403)
                        except ImportError:
                            return JsonResponse({'error': 'Access denied'}, status=403)
                elif model_name == 'user':
                    if int(resource_id) != user.id:
                        try:
                            from rest_framework.response import Response
                            return Response({'error': 'Access denied'}, status=403)
                        except ImportError:
                            return JsonResponse({'error': 'Access denied'}, status=403)
                else:
                    try:
                        from rest_framework.response import Response
                        return Response({'error': 'Invalid resource type'}, status=400)
                    except ImportError:
                        return JsonResponse({'error': 'Invalid resource type'}, status=400)
            except (Applicant.DoesNotExist, Company.DoesNotExist, User.DoesNotExist):
                try:
                    from rest_framework.response import Response
                    return Response({'error': 'Resource not found'}, status=404)
                except ImportError:
                    return JsonResponse({'error': 'Resource not found'}, status=404)
            
            request.user = user
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
