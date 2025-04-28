from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cloudinary_storage.storage import RawMediaCloudinaryStorage, MediaCloudinaryStorage, VideoMediaCloudinaryStorage


def user_folder(instance, filename):
    folder_path =  f"powerup/users/{instance.user.username}/{filename}"
    return folder_path

class UserImageFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="image_files", null=True)
    url = models.ImageField(verbose_name= 'Image', blank=False, upload_to=user_folder, null=True, storage=MediaCloudinaryStorage() if not settings.DEBUG else None)
    filename = models.CharField(max_length=255, verbose_name='Filename', blank=False, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.filename} : {self.url}"
    

# Create your models here.
class WorkoutType(models.Model):
    WORKOUT_CHOICES = [
        ('running', 'Running'),
        ('walking', 'Walking'),
        ('cycling', 'Cycling'),
        ('hiking', 'Hiking'),
        ('bodyweight', 'Bodyweight Training'),
        ('hiit', 'HIIT Workout'),
        ('yoga', 'Yoga/Stretching'),
    ]
    name = models.CharField(max_length=50, unique=True, choices=WORKOUT_CHOICES)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='powerup/workout_types/thumbnails/', blank=True, null=True, storage=MediaCloudinaryStorage() if not settings.DEBUG else None)
    animation = models.FileField(upload_to='powerup/workout_types/animations/', blank=True, null=True, storage=VideoMediaCloudinaryStorage() if not settings.DEBUG else None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    img = models.ForeignKey(UserImageFile, on_delete=models.SET_NULL, null=True, verbose_name="User image", related_name="profile_images")
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)


class Workout(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="workouts", null=True)
    workout_type = models.ForeignKey(WorkoutType, on_delete=models.CASCADE, verbose_name="Workout Type")
    duration = models.FloatField(help_text="Duration in minutes", default=0)
    calories_burned = models.FloatField(blank=True, default=0)
    img = models.ForeignKey(UserImageFile, on_delete=models.SET_NULL, null=True, verbose_name="User selfie image", related_name="workout_images")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f" - {self.workout_type} on {self.created_at.date()}"

