from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
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
    name = models.CharField(max_length=50, unique=True, choices=WORKOUT_CHOICES, verbose_name="Workout Type Name")
    description = models.TextField(blank=True, null=True, verbose_name="Workout Description")
    calories_burned_per_minute = models.FloatField(blank=True, default=6, verbose_name="Calories Burn Rate Per Minute")
    points_per_minute = models.FloatField(blank=True, default=5, verbose_name="Points Earned Per Minute")
    thumbnail = models.ImageField(upload_to='powerup/workout_types/thumbnails/', blank=True, null=True, storage=MediaCloudinaryStorage() if not settings.DEBUG else None)
    animation = models.FileField(upload_to='powerup/workout_types/animations/', blank=True, null=True, storage=VideoMediaCloudinaryStorage() if not settings.DEBUG else None)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    img = models.ForeignKey(UserImageFile, on_delete=models.SET_NULL, null=True, verbose_name="User image", related_name="profile_images")
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=50, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], null=True, blank=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True, verbose_name="Age")
    height = models.FloatField(blank=True, null=True, verbose_name="Height")
    weight = models.FloatField(blank=True, null=True, verbose_name="Weight")
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.user.username if self.user else None

class Workout(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="workouts", null=True)
    workout_type = models.ForeignKey(WorkoutType, on_delete=models.CASCADE, verbose_name="Workout Type", related_name="workouts")
    duration = models.FloatField(help_text="Duration in Secondes", verbose_name="Duration", default=0)
    calories_burned = models.FloatField(blank=True, default=0, verbose_name="Calories Burned")
    points = models.FloatField(blank=True, default=0, verbose_name="Points Earned")
    img = models.ForeignKey(UserImageFile, on_delete=models.SET_NULL, null=True, verbose_name="User selfie image", related_name="workout_images")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.profile} - {self.workout_type} on {self.created_at.date()}"


class Community(models.Model):
    name = models.CharField(max_length=255, verbose_name="Community Name")
    description = models.TextField(blank=True, null=True, verbose_name="Community Description")
    img = models.ForeignKey(UserImageFile, on_delete=models.SET_NULL, null=True, verbose_name="Community Profile Image", related_name="communities")
    admins = models.ManyToManyField(Profile, related_name='admin_communities', blank=True, verbose_name="Community Admins")
    members = models.ManyToManyField(Profile, related_name='communities', blank=True, verbose_name="Community Members")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Challenge(models.Model):
    name = models.CharField(max_length=255, verbose_name='Challenge Name')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="challenges")
    description = models.TextField(blank=True, null=True, verbose_name='Challenge Description')
    workout_type = models.ForeignKey(WorkoutType, on_delete=models.CASCADE, related_name="challenges", verbose_name="Workout Type")
    start_date = models.DateField(auto_now_add=True, verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    
    class Meta:
        ordering = ['-id']

class ChallengeParticipant(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="challenge_participants")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="participants")
    progress = models.FloatField(default=0, verbose_name="Progress")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Joined At")
