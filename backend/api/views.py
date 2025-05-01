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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Django Restframework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

# Other
from api.models import *
from api.serializer import *
from api.utils import log_error, delete_file
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
        
    return Response(user_data, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_app_data(request):
    workout_types = WorkoutTypeSerializerOne(WorkoutType.objects.all(), many=True)
    current_year = timezone.now().year

    return Response({
        'workout_types': workout_types.data,
        'current_year_start_date': datetime(current_year, 1, 1).strftime("%Y-%m-%d"),
        'current_year_end_date': datetime(current_year, 12, 31).strftime("%Y-%m-%d"),
    }, status=200)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_user_workout_data(request):
    user = request.user
    if request.method == 'GET':
        profile = Profile.objects.get(user=request.user)
        workouts_data = WorkoutSerializerOne(Workout.objects.filter(profile=profile), many=True).data

        return Response({
            'workouts': workouts_data,
        }, status=200)
    
    else:
        data = request.data
        if data['type'] == 'createWorkout':
            selfie = data['selfie']
            profile = Profile.objects.get(user=user)
            if not imghdr.what(selfie):
                return Response({'message': 'Invalid image format'}, status=400)
            
            workout_type = WorkoutType.objects.get(id=int(data['workoutType']))
            points_earned = float(data['pointsEarned'])
            calories_burned = float(data['caloriesBurned'])
            duration = float(data['duration'])

            with transaction.atomic():
                try:
                    selfie = UserImageFile.objects.create(
                        user=user,
                        url=selfie,
                        filename=selfie.name,
                    )
                    workout = Workout.objects.create(
                        profile=profile,
                        workout_type=workout_type,
                        duration=duration,
                        img=selfie,
                        date=timezone.now().date(),
                        calories_burned=calories_burned,
                        points=points_earned,
                    )
                    return Response(WorkoutSerializerOne(workout).data, status=200)
                except Exception as e:
                    transaction.set_rollback(True)
                    log_error(e)
                    delete_file(selfie)
                    return Response(status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data
    data_obj = json.loads(data['dataObj'])
    email = data_obj.get('email').strip()
    if User.objects.filter(email=email).exists():
        return Response({'message': 'A user with that email address already exists. Please login if you already have an account.'}, status=400)
    
    first_name = data_obj.get('first_name').strip().title()
    last_name = data_obj.get('last_name').strip().title()
    username = data_obj.get('username').strip()
    password = data_obj.get('password').strip()
    age = int(data_obj.get('age'))
    gender = data_obj.get('gender').strip()
    country = data_obj.get('country').strip()
    city = data_obj.get('city').strip()
    height = float(data_obj.get('height')) if data_obj.get('height') and data_obj.get('height') != 'null' else None
    weight = float(data_obj.get('weight')) if data_obj.get('weight') and data_obj.get('weight') != 'null' else None
    bio = data_obj.get('bio').strip() if data_obj.get('bio') and data_obj.get('bio') != 'null' else None
    img = data['userImage'] if data['userImage'] and data['userImage'] != 'null' else None
    if img and not imghdr.what(img):
        return Response({'message': 'Invalid image file. Ensure you upload a valid image file or remove the image'}, status=400)
    
    with transaction.atomic():
        try:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            if img:
                img = UserImageFile.objects.create(
                    user=user,
                    url=img,
                    filename=img.name,
                )
            Profile.objects.create(
                user=user,
                age=age,
                gender=gender,
                height=height,
                weight=weight,
                country=country,
                city=city,
                bio=bio,
                img=img if img else None,
            )
            subject = "Welcome to PowerUp! 🚀"
            to_email = user.email
            context = {"first_name": user.first_name, "app_url": "https://powerup.onrender.com", 'support_email': os.environ.get('EMAIL_HOST_USER'), 'logo_url': 'https://res.cloudinary.com/dbrgcxign/image/upload/v1745955648/0d51667561df5170ba0bcd0523ed28bf_slkgym.webp'}
            html_content = render_to_string("welcome_email.html", context)
            email_sender = formataddr((os.environ.get('EMAIL_SENDER_NAME'), os.environ.get('EMAIL_HOST_USER')))
            try:
                send_email = EmailMultiAlternatives(subject, "", email_sender, [to_email])
                send_email.attach_alternative(html_content, "text/html")
                send_email.send(fail_silently=False)
            except Exception as e:
                transaction.set_rollback(True)
                log_error(e)
                if img:
                    delete_file(img)
                return Response({'message': 'A network error occurred. Please check your internet connection and try again.'}, status=400)
            
            return Response(status=201)
        
        except IntegrityError:
            transaction.set_rollback(True)
            log_error(e)
            if img:
                delete_file(img)
            return Response({'message': 'A user with that username already exists. Please choose a different username.'}, status=400)
        except Exception as e:
            transaction.set_rollback(True)
            log_error(e)
            if img:
                delete_file(img)
            return Response(status=400)

