# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/users/views.py
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from .models import UserProfile
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
from django.http import JsonResponse


class UserRegistrationView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        return Response({
            'message': '登录成功',
            'user': UserProfileSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_logout(request):
    logout(request)
    return Response({'message': '登出成功'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_csrf_token(request):
    """获取CSRF token"""
    token = get_token(request)
    return JsonResponse({'csrfToken': token})

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user