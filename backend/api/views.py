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
from django.db.models import Q, Prefetch

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
from api.utils import log_error, delete_file, use_pusher, valid_email
from datetime import datetime
import json
import imghdr
import traceback


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
        'username': user.username,
        'last_login': user.last_login,
        'email': user.email,
    }
    profile = Profile.objects.select_related('img').get(user=user)
    user_data.update(ProfileSerializer(profile).data)
        
    return Response(user_data, status=200)


@api_view(['GET'])
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
        communities = CommunitySerializerOne(Community.objects.select_related('img').prefetch_related(
            Prefetch('admins', queryset=Profile.objects.select_related('user', 'img').all()), 
            Prefetch('members', queryset=Profile.objects.select_related('user', 'img').all()),
            Prefetch('challenges', queryset=Challenge.objects.prefetch_related('workout_types', Prefetch('participants', queryset=ChallengeParticipant.objects.select_related('profile__user').all()),).all()),
        ).filter(members=profile), many=True).data

        return Response({
            'workouts': workouts_data,
            'communities': communities,
        }, status=200)
    
    else:
        data = request.data
        if data['type'] == 'createWorkout':
            selfie = data['selfie']
            profile = Profile.objects.get(user=user)
            if not imghdr.what(selfie):
                return Response({'message': 'Invalid image format'}, status=400)
            
            workout_type = WorkoutType.objects.get(id=int(data['workoutType']))
            points_earned, calories_burned, duration = float(data['pointsEarned']), float(data['caloriesBurned']), float(data['duration'])

            with transaction.atomic():
                try:
                    selfie = UserImageFile.objects.create(user=user, url=selfie, filename=selfie.name,)
                    workout = Workout.objects.create(
                        profile=profile,
                        workout_type=workout_type,
                        duration=duration,
                        img=selfie,
                        date=timezone.now().date(),
                        calories_burned=calories_burned,
                        points=points_earned,
                    )
                    current_date = timezone.now().date()
                    challenges = Challenge.objects.filter(workout_types=workout_type, start_date__lte=current_date, end_date__gte=current_date)
                    challenge_participants = ChallengeParticipant.objects.filter(challenge__in=challenges, profile=profile)
                    for challenge_participant in challenge_participants:
                        challenge_participant.points += points_earned
                        challenge_participant.save()
                    return Response(WorkoutSerializerOne(workout).data, status=200)
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    delete_file(selfie)
                    return Response(status=400)
                
        elif data['type'] == 'createCommunity':
            profile = Profile.objects.get(user=user)
            community_image = data['communityImage'] if data['communityImage'] and data['communityImage'] != 'null' else ''
            data_obj = json.loads(data['dataObj'])
            name, description = data_obj.get('name').strip(), data_obj.get('description').strip()
            if community_image and not imghdr.what(community_image):
                return Response({'message': 'Invalid image format'}, status=400)
       
            with transaction.atomic():
                try:
                    if community_image:
                        community_image = UserImageFile.objects.create(
                            user=user,
                            url=community_image,
                            filename=community_image.name,
                        )
                    item_to_create = Community.objects.create(
                        name=name,
                        description=description,
                        img=community_image if community_image else None,
                    )
                    item_to_create.admins.add(profile)
                    item_to_create.members.add(profile)
                    return Response(CommunitySerializerOne(Community.objects.select_related('img').prefetch_related(
                        Prefetch('admins', queryset=Profile.objects.select_related('user', 'img').all()), 
                        Prefetch('members', queryset=Profile.objects.select_related('user', 'img').all()),
                        Prefetch('challenges', queryset=Challenge.objects.prefetch_related('workout_types', Prefetch('participants', queryset=ChallengeParticipant.objects.select_related('profile__user').all()),).all()),
                    ).get(id=item_to_create.id)).data, status=200)
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    if community_image:
                        delete_file(community_image)
                    return Response(status=400)

        elif data['type'] == 'addCommunityAdmin':
            profile = Profile.objects.get(user=user)
            new_admin = Profile.objects.select_related('user').get(id=int(data['memberId']))
            community = Community.objects.prefetch_related('admins').get(id=int(data['communityId']))
            if profile not in community.admins.all():
                return Response({'message': 'You are not an admin of this community'}, status=400)
            elif new_admin in community.admins.all():
                return Response({'message': f"The member you selected is already an admin"}, status=400)
       
            with transaction.atomic():
                try:
                    community.admins.add(new_admin)
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)

            return Response(status=204)

        elif data['type'] == 'removeCommunityAdmin':
            profile = Profile.objects.get(user=user)
            old_admin = Profile.objects.select_related('user').get(id=int(data['adminId']))
            community = Community.objects.prefetch_related('admins').get(id=int(data['communityId']))
            if profile not in community.admins.all():
                return Response({'message': 'You are not an admin of this community'}, status=400)
       
            with transaction.atomic():
                try:
                    community.admins.remove(old_admin)
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)

            return Response(status=204)
        
        elif data['type'] == 'addCommunityMember':
            profile = Profile.objects.get(user=user)
            new_member_user = User.objects.filter(username=data['username']).first()
            if not new_member_user:
                return Response({'message': 'Oops! There is no account associated with this username'}, status=400)
            new_member = Profile.objects.get(user=new_member_user)
            community = Community.objects.prefetch_related('admins', 'members').get(id=int(data['communityId']))
            if profile not in community.admins.all():
                return Response({'message': 'You are not an admin of this community'}, status=400)
            elif new_member in community.members.all():
                return Response({'message': f"The member you selected is already a member of the community"}, status=400)
       
            with transaction.atomic():
                try:
                    community.members.add(new_member)
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)
                
            return Response(ProfileSerializerOne(new_member).data, status=200)
        
        elif data['type'] == 'removeCommunityMember':
            profile = Profile.objects.get(user=user)
            member = Profile.objects.select_related('user').get(id=int(data['memberId']))
            community = Community.objects.prefetch_related('admins').get(id=int(data['communityId']))
            if profile not in community.admins.all():
                return Response({'message': 'You are not an admin of this community'}, status=400)
            elif member in community.admins.all():
                return Response({'message': 'You cannot remove a member who is an admin. Remove the person from the community admin before'}, status=400)
       
            with transaction.atomic():
                try:
                    RemovedCommunityMember.objects.create(profile=member, community=community, date=timezone.now().date())
                    community.members.remove(member)
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)

            return Response(status=204)
        
        elif data['type'] == 'joinCommunity':
            profile = Profile.objects.get(user=user)
            data_obj = json.loads(data['dataObj'])
            community = Community.objects.prefetch_related('members').filter(join_code=data_obj.get('join_code')).first()
            if not community:
                return Response({'message': 'Oops! That community code is invalid or has been removed.'}, status=400)
            elif community and profile in community.members.all():
                return Response({'message': f"You are already a member of the community '{community.name}'"}, status=400)
            elif RemovedCommunityMember.objects.filter(profile=profile, community=community).exists():
                return Response({'message': f"You were removed from the community '{community.name}'. You cannot join using the community code"}, status=400)
       
            with transaction.atomic():
                try:
                    community.members.add(profile)
                    return Response(CommunitySerializerOne(Community.objects.select_related('img').prefetch_related(
                        Prefetch('admins', queryset=Profile.objects.select_related('user', 'img').all()), 
                        Prefetch('members', queryset=Profile.objects.select_related('user', 'img').all()),
                        Prefetch('challenges', queryset=Challenge.objects.prefetch_related('workout_types', Prefetch('participants', queryset=ChallengeParticipant.objects.select_related('profile__user').all()),).all()),
                    ).get(id=community.id)).data, status=200)
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)
        
        
        elif data['type'] == 'exitCommunity':
            profile = Profile.objects.get(user=user)
            community = Community.objects.prefetch_related('members').get(id=int(data['communityId']))
       
            with transaction.atomic():
                try:
                    community.members.remove(profile)
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)
                
        elif data['type'] == 'deleteCommunity':
            profile = Profile.objects.select_related('user').get(user=user)
            community = Community.objects.prefetch_related('admins').get(id=int(data['itemId']))
            channel = f"community_{community.id}"
            if profile not in community.admins.all():
                return Response({'message': 'You are not authorized to delete this community'}, status=400)
       
            with transaction.atomic():
                try:
                    if community.img:
                        community.img.delete()
                    community.delete()
                except Exception as e:
                    transaction.set_rollback(True)
                    log_error(e)
                    return Response(status=400)
            
            try:
                pusher = use_pusher()
                pusher.trigger(channel, 'community_deleted', profile.user.username)
            except Exception:
                log_error(traceback.format_exc())
            return Response(status=204)

        elif data['type'] == 'createChallenge':
            profile = Profile.objects.select_related('user').get(user=user)
            community = Community.objects.prefetch_related('admins').get(id=int(data['communityId']))
            data_obj = json.loads(data['dataObj'])
            name, description, start_date, end_date = data_obj.get('name').strip(), data_obj.get('description').strip(), data_obj.get('start_date'), data_obj.get('end_date')
            if profile not in community.admins.all():
                return Response({'message': 'You are not authorized to create a challenge in this community'}, status=400)
            
            if datetime.fromisoformat(start_date) > datetime.fromisoformat(end_date):
                return Response({'message': 'The start date cannot be after the end date'}, status=400)
            
            workout_types = WorkoutType.objects.filter(id__in=[int(x) for x in data_obj.get('workout_types')])
            item_to_create = None
            with transaction.atomic():
                try:
                    item_to_create = Challenge.objects.create(
                        name=name,
                        description=description,
                        start_date=start_date,
                        end_date=end_date,
                        date=timezone.now().date(),
                        community=community,
                    )
                    item_to_create.workout_types.set(workout_types)
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)
            
            challenge = Challenge.objects.prefetch_related('workout_types',
                Prefetch('participants', queryset=ChallengeParticipant.objects.select_related('profile__user').all()), 
            ).get(id=item_to_create.id)
            challenge_data = ChallengeSerializerOne(challenge).data
            channel, challenge_id, challenge_name = f"community_{challenge.community.id}", challenge.id, challenge.name
            try:
                pusher = use_pusher()
                pusher.trigger(channel, 'challenge_added', {'challenge': challenge_data, 'username': profile.user.username})
            except Exception:
                log_error(traceback.format_exc())

            return Response(challenge_data, status=200)
        
        elif data['type'] == 'joinChallenge':
            profile = Profile.objects.get(user=user)
            challenge = Challenge.objects.prefetch_related('participants').get(id=int(data['challengeId']))
            item_to_create = None
            with transaction.atomic():
                try:
                    item_to_create = ChallengeParticipant.objects.create(profile=profile, challenge=challenge, date_joined=timezone.now().date())
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)
            return Response(ChallengeParticipantSerializerOne(ChallengeParticipant.objects.select_related('profile__user').get(id=item_to_create.id)).data, status=200)
        
        elif data['type'] == 'exitChallenge':
            profile = Profile.objects.get(user=user)
            challenge = Challenge.objects.prefetch_related('participants').get(id=int(data['challengeId']))
            challenge_participant = ChallengeParticipant.objects.get(profile=profile, challenge=challenge)
            challenge_participant_data = ChallengeParticipant(challenge_participant).data
            with transaction.atomic():
                try:
                    challenge_participant.delete()
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)
                
            return Response(challenge_participant_data, status=200)
        
        elif data['type'] == 'deleteChallenge':
            profile = Profile.objects.select_related('user').get(user=user)
            challenge = Challenge.objects.select_related('community').prefetch_related('community__admins').get(id=int(data['itemId']))
            channel, challenge_id, challenge_name = f"community_{challenge.community.id}", challenge.id, challenge.name
            if profile not in challenge.community.admins.all():
                return Response({'message': 'You are not authorized to delete this challenge'}, status=400)
       
            with transaction.atomic():
                try:
                    challenge.delete()
                except Exception:
                    transaction.set_rollback(True)
                    log_error(traceback.format_exc())
                    return Response(status=400)

            try:
                pusher = use_pusher()
                pusher.trigger(channel, 'challenge_deleted', {'challenge_id': challenge_id, 'challenge_name': challenge_name, 'username': profile.user.username})
            except Exception:
                log_error(traceback.format_exc())
            return Response(status=204)


@api_view(['POST'])
def register_user(request):
    data = request.data
    data_obj = json.loads(data['dataObj'])
    email, username, password = data_obj.get('email').strip(), data_obj.get('username').strip(), data_obj.get('password').strip()
    img = data['userImage'] if data['userImage'] and data['userImage'] != 'null' else None
    if img and not imghdr.what(img):
        return Response({'message': 'Invalid image file. Ensure you upload a valid image file or remove the image'}, status=400)
    if not valid_email(email):
        return Response({'message': "Invalid email address. Check your email address and ensure it's valid"}, status=400)
    if User.objects.filter(email=email).exists():
        return Response({'message': 'A user with that email address already exists. Please login if you already have an account.'}, status=400)
    
    age, gender, country, city = int(data_obj.get('age')), data_obj.get('gender').strip(), data_obj.get('country').strip(), data_obj.get('city').strip()
    height = float(data_obj.get('height')) if data_obj.get('height') and data_obj.get('height') != 'null' else None
    weight = float(data_obj.get('weight')) if data_obj.get('weight') and data_obj.get('weight') != 'null' else None
    bio = data_obj.get('bio').strip() if data_obj.get('bio') and data_obj.get('bio') != 'null' else None
    
    with transaction.atomic():
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            if img:
                img = UserImageFile.objects.create(user=user, url=img, filename=img.name)
            Profile.objects.create(user=user, age=age, gender=gender, height=height, weight=weight, country=country, city=city, bio=bio, img=img if img else None)
            subject = "Welcome to PowerUp! 🚀"
            to_email = user.email
            context = {"first_name": user.first_name, "app_url": "https://powerup.onrender.com", 'support_email': os.environ.get('EMAIL_HOST_USER'), 'logo_url': 'https://res.cloudinary.com/dbrgcxign/image/upload/v1745955648/0d51667561df5170ba0bcd0523ed28bf_slkgym.webp'}
            html_content = render_to_string("welcome_email.html", context)
            email_sender = formataddr((os.environ.get('EMAIL_SENDER_NAME'), os.environ.get('EMAIL_HOST_USER')))
            try:
                send_email = EmailMultiAlternatives(subject, "", email_sender, [to_email])
                send_email.attach_alternative(html_content, "text/html")
                send_email.send(fail_silently=False)
            except Exception:
                transaction.set_rollback(True)
                log_error(traceback.format_exc())
                if img:
                    delete_file(img)
                return Response({'message': 'A network error occurred. Please check your internet connection and try again.'}, status=400)
            
            return Response(status=201)
        
        except IntegrityError:
            transaction.set_rollback(True)
            if img:
                delete_file(img)
            return Response({'message': 'A user with that username already exists. Please choose a different username.'}, status=400)
        except Exception:
            transaction.set_rollback(True)
            log_error(traceback.format_exc())
            if img:
                delete_file(img)
            return Response(status=400)

