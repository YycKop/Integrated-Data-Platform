# Copyright (c) 2025 YycKop
# MIT License
# Integrated-Data-Platform-backend/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password', 'password_confirm', 'role', 'phone', 'department')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "密码不匹配"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = UserProfile.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('必须提供用户名和密码')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'role', 'phone', 'department', 'date_joined')
        read_only_fields = ('id', 'date_joined')