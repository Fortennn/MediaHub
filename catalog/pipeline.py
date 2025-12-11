import os
import urllib.request
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from django.utils.crypto import get_random_string
from .models import Profile


def save_avatar(backend, user, response, *args, **kwargs):
    """Fetch and store Google avatar on first login (or when missing)."""
    if backend.name != 'google-oauth2':
        return

    avatar_url = response.get('picture')
    if not avatar_url:
        return

    profile, _ = Profile.objects.get_or_create(user=user)
    if profile.avatar:
        return

    try:
        with NamedTemporaryFile(delete=True) as temp_file:
            with urllib.request.urlopen(avatar_url) as resp:
                temp_file.write(resp.read())
            temp_file.flush()
            temp_file.seek(0)

            ext = os.path.splitext(avatar_url.split('?')[0])[1] or '.jpg'
            filename = f"google_{user.pk}_{get_random_string(8)}{ext}"
            profile.avatar.save(filename, ContentFile(temp_file.read()), save=True)
    except Exception:
        return
