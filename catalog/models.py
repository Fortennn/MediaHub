from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
import uuid
from django.core.files.storage import default_storage

def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('avatars', new_filename)


class Genre(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class MediaItem(models.Model):
    MEDIA_TYPES = [
        ('movie', 'Фільм'),
        ('series', 'Серіал'),
        ('anime', 'Аніме'),
    ]

    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    release_year = models.IntegerField()
    country = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Тривалість у хвилинах")
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    trailer_url = models.URLField(blank=True)
    genres = models.ManyToManyField(Genre)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['media_type']),
        ]

    def __str__(self):
        return self.title

    def average_rating(self):
        return self.ratings.aggregate(models.Avg('score'))['score__avg'] or 0

class Season(models.Model):
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name='seasons')
    season_number = models.IntegerField()
    title = models.CharField(max_length=255, blank=True)
    release_year = models.IntegerField()
    episodes_count = models.IntegerField(default=0, help_text="Кількість епізодів у сезоні")

    class Meta:
        ordering = ['season_number']
        unique_together = ['media_item', 'season_number']

    def __str__(self):
        return f"{self.media_item.title} - Сезон {self.season_number}"

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'media_item']
        ordering = ['-created_at']

class Watchlist(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'planned', 'В планах'
        WATCHED = 'watched', 'Переглянуто'
        FAVORITE = 'favorite', 'Улюблене'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'media_item']
        ordering = ['-added_at']


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True) 

    def __str__(self):
        return f'Profile for {self.user.username}'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(models.signals.pre_save, sender=Profile)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    """Remove previous avatar file when a new one is set."""
    if not instance.pk:
        return
    try:
        old_avatar = Profile.objects.get(pk=instance.pk).avatar
    except Profile.DoesNotExist:
        return
    new_avatar = instance.avatar
    if old_avatar and new_avatar and old_avatar.name != new_avatar.name:
        if default_storage.exists(old_avatar.name):
            default_storage.delete(old_avatar.name)
