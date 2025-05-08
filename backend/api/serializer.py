from pathlib import Path
from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings
from backend.production import ALLOWED_HOSTS
from api.models import *

BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTION_DOMAIN = ALLOWED_HOSTS[0]

def get_default_image(default_img:str=''):
    if default_img == 'staff_img':
        default_img = 'staff_img.jpg'
    elif default_img == 'app_logo':
        default_img = 'app_logo.png'
    
    img = ''
    if settings.DEBUG:
        img = f"http://localhost:8000/static/images/{default_img}"
    else:
        img = f"https://{PRODUCTION_DOMAIN}/static/images/{default_img}"
    
    return img


def get_file_url(url):
    if settings.DEBUG:
        if url and url != 'null':
            url = f"http://localhost:8000{url}"
    
    return url


class UserImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImageFile
        fields = ('url', 'filename', 'id')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['url'] = get_file_url(data['url'])
        
        return data


# Profile
class ProfileSerializer(serializers.ModelSerializer):
    img = UserImageFileSerializer()

    class Meta:
        model = Profile
        exclude = ["user"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['img']:
            data['img'] = get_default_image('staff_img')
               
        return data


class ProfileSerializerOne(serializers.ModelSerializer):
    img = UserImageFileSerializer()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        exclude = ["created_at"]

    def get_user(self, obj):
        return {
            'username': obj.user.username,
            'email': obj.user.email,
        }
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['img']:
            data['img'] = get_default_image('staff_img')
        else:
            data['img'] = data['img']['url']

        return {
            'id': data['id'],
            'username': data['user']['username'],
            'email': data['user']['email'],
            'gender': data['gender'],
            'bio': data['bio'],
            'country': data['country'],
            'city': data['city'],
            'age': data['age'],
            'height': data['height'],
            'weight': data['weight'],
            'img': data['img'],
        }


# Workout Type Serializers
class WorkoutTypeSerializerOne(serializers.ModelSerializer):
    class Meta:
        model = WorkoutType
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['thumbnail']:
            data['thumbnail'] = get_default_image('app_logo')
        else:
            data['thumbnail'] = get_file_url(data['thumbnail'])
        if data['animation']:
            data['animation'] = get_file_url(data['animation'])

        return data


# Workout Serializers
class WorkoutSerializerOne(serializers.ModelSerializer):
    img = UserImageFileSerializer()
    workout_type = serializers.SerializerMethodField()

    class Meta:
        model = Workout
        exclude = ["profile"]
    
    def get_workout_type(self, obj):
        return obj.workout_type.name
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['img']:
            data['img'] = get_default_image('app_logo')
               
        return data


# Community Serializers
class CommunitySerializerOne(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    admins = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    challenges = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = "__all__"
    
    def get_admins(self, obj):
        return [{
            'id': item.id,
            'username': item.user.username,
            'email': item.user.email,
            'gender': item.gender,
            'bio': item.bio,
            'country': item.country,
            'city': item.city,
            'age': item.age,
            'height': item.height,
            'weight': item.weight,
            'img': UserImageFileSerializer(item.img).data['url'] if item.img else get_default_image('staff_img'),
        } for item in obj.admins.all()]
    
    def get_members(self, obj):
        return [{
            'id': item.id,
            'username': item.user.username,
            'email': item.user.email,
            'gender': item.gender,
            'bio': item.bio,
            'country': item.country,
            'city': item.city,
            'age': item.age,
            'height': item.height,
            'weight': item.weight,
            'img': UserImageFileSerializer(item.img).data['url'] if item.img else get_default_image('staff_img'),
        } for item in obj.members.all()]
    
    def get_img(self, obj):
        return UserImageFileSerializer(obj.img).data['url'] if obj.img else get_default_image('app_logo')
    
    def get_challenges(self, obj):
        return [{
            'id': challenge.id,
            'name': challenge.name,
            'description': challenge.description,
            'workout_types': [x.name for x in challenge.workout_types.all()],
            'start_date': challenge.start_date,
            'end_date': challenge.end_date,
            'date': challenge.date,
            'participants': [{
                'id': participant.id,
                'username': participant.profile.user.username,
                'points': participant.points,
                'date_joined': participant.date_joined,
            } for participant in challenge.participants.all()]
        } for challenge in obj.challenges.all()]


# Challenge Serializers
class ChallengeSerializerOne(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    workout_types = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        exclude = ["community"]
    
    def get_workout_types(self, obj):
        return [x.name for x in obj.workout_types.all()]
    
    def get_participants(self, obj):
        return [{
            'id': participant.id,
            'username': participant.profile.user.username,
            'points': participant.points,
            'date_joined': participant.date_joined,
        } for participant in obj.participants.all()]


# Challenge Participant Serializers
class ChallengeParticipantSerializerOne(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = ChallengeParticipant
        exclude = ["challenge"]
    
    def get_profile(self, obj):
        return obj.profile.user.username
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
               
        return {
            'id': data['id'],
            'username': data['profile'],
            'date_joined': data['date_joined'],
            'points': data['points'],
        }

