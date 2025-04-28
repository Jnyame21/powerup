from pathlib import Path
from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings
from backend.production import ALLOWED_HOSTS
from api.models import *
from api.utils import format_relative_date_time

BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTION_DOMAIN = ALLOWED_HOSTS[0]

def get_default_image(default_img:str=''):
    if default_img == 'staff_img':
        default_img = 'staff_img.jpg'
    elif default_img == 'business_logo':
        default_img = 'business_logo.png'
    
    img = ''
    if settings.DEBUG:
        img = f"http://localhost:8000/static/images/{default_img}"
    else:
        img = f"https://{PRODUCTION_DOMAIN}/static/images/{default_img}"
    
    return img


def get_file_url(data, property_reference):
    url = data[property_reference]
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
        data['url'] = get_file_url(data, 'url')
        
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


# Workout Type Serializers
class WorkoutTypeSerializerOne(serializers.ModelSerializer):
    class Meta:
        model = WorkoutType
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['thumbnail']:
            data['thumbnail'] = get_default_image('business_logo')
               
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
            data['img'] = get_default_image('business_logo')
               
        return data

