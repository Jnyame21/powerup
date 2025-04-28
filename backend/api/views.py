import os
# Django
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.db import transaction, IntegrityError
from django.core.mail import EmailMessage
from email.utils import formataddr
from email.mime.image import MIMEImage

# Django Restframework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

# Other
from api.models import *
from api.serializer import *
from datetime import datetime
import json
import imghdr

def root(request):
    return HttpResponse("<h1>NexaSuite</h1>")


@api_view(['GET'])
def get_current_server_time(request):
    return Response({'timestamp': timezone.now().timestamp(), 'current_date': timezone.now().date()}, status=200)


@api_view(['POST'])
def refresh_server(request):
    return Response(status=200)


# LOGIN
class UserAuthSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        return token


class UserAuthView(TokenObtainPairView):
    serializer_class = UserAuthSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.get('refresh')
        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                expires = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.DEBUG is False,
                samesite="Lax" if settings.DEBUG else "None",
                path="/",
            )
            del response.data['refresh']

        return response


# Refresh Token
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            raise AuthenticationFailed("You have been logged out")

        request.data["refresh"] = refresh_token
        response = super().post(request, *args, **kwargs)
    
        if response.status_code == 200:
            new_refresh_token = response.data['refresh']
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                secure=settings.DEBUG is False,
                samesite="Lax" if settings.DEBUG else "None",
                path="/",
                expires = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            )
            del response.data['refresh']

        return response


# Logout
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        return Response({'message': 'Missing refresh token'}, status=401)
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return Response({'message': 'Invalid refresh token'}, status=400)
    
    response = Response(status=200)
    response.delete_cookie("refresh_token", path="/")
    return response


# Reset password
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_user_password(request):
    user = request.user
    user.set_password(request.data['password'])
    if check_password(user.username, user.password):
        return Response({'message': "The password cannot be the same as the username"}, status=400)
    
    user.save()
    
    return Response(status=204)


# User Data
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    user = request.user
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'last_login': user.last_login,
        'email': user.email,
    }
    profile = Profile.objects.select_related('img').get(user=user)
    user_data.update(ProfileSerializer(profile).data)
    current_year = timezone.now().year
    user_data['current_year_start_date'] = datetime(current_year, 1, 1).strftime("%Y-%m-%d")
    user_data['current_year_end_date'] = datetime(current_year, 12, 31).strftime("%Y-%m-%d")
        
    return Response(user_data, status=200)


@api_view(['GET'])
def get_app_data(request):
    workout_types = WorkoutTypeSerializerOne(WorkoutType.objects.all(), many=True)
    return Response({
        'workout_types': workout_types.data,
    }, status=200)

