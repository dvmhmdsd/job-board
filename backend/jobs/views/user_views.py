from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from ..models import User
from ..auth import require_authentication, require_ownership_or_admin, hash_password


@method_decorator(csrf_exempt, name='dispatch')
class UserListView(View):
    @require_authentication
    def get(self, request):
        """Get all users - Admin only for now"""
        users = User.objects.all()
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'name': user.name
            })
        return JsonResponse({'users': users_data})
    
    def post(self, request):
        """Create a new user - Use /auth/register instead"""
        return JsonResponse({'error': 'Use /auth/register endpoint for user registration'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(View):
    @require_ownership_or_admin('user', 'user_id')
    def get(self, request, user_id):
        """Get a specific user - Owner only"""
        user = get_object_or_404(User, id=user_id)
        return JsonResponse({
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'name': user.name
        })
    
    @require_ownership_or_admin('user', 'user_id')
    def put(self, request, user_id):
        """Update a specific user - Owner only"""
        try:
            user = get_object_or_404(User, id=user_id)
            data = json.loads(request.body)
            
            user.email = data.get('email', user.email)
            if 'password' in data:
                user.password_hash = hash_password(data['password'])
            user.role = data.get('role', user.role)
            user.name = data.get('name', user.name)
            user.save()
            
            return JsonResponse({
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'name': user.name
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    @require_ownership_or_admin('user', 'user_id')
    def delete(self, request, user_id):
        """Delete a specific user - Owner only"""
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return JsonResponse({'message': 'User deleted successfully'}, status=204)
