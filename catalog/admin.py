from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from .models import Genre, MediaItem, Season, Rating, Watchlist, Profile


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'media_type', 'release_year', 'country', 'is_published']
    list_filter = ['media_type', 'genres', 'is_published', 'release_year']
    search_fields = ['title', 'original_title', 'description', 'country']
    save_on_top = True
    filter_horizontal = ['genres']
    radio_fields = {'media_type': admin.HORIZONTAL}
    readonly_fields = ['poster_preview', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic info', {
            'fields': ('title', 'original_title', 'media_type', 'description'),
        }),
        ('Release', {
            'fields': (('release_year', 'country', 'duration'),),
        }),
        ('Media', {
            'fields': ('poster', 'poster_preview', 'trailer_url'),
        }),
        ('Categories', {
            'fields': ('genres',),
        }),
        ('Status', {
            'fields': ('is_published', 'created_at', 'updated_at'),
        }),
    )

    class Media:
        css = {'all': ('admin/custom-admin.css',)}

    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" width="100" />', obj.poster.url)
        return ""
    poster_preview.short_description = "Poster preview"


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['media_item', 'season_number', 'title', 'release_year', 'episodes_count']
    list_filter = ['media_item', 'release_year']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'media_item', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['user__username', 'media_item__title']


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'media_item', 'added_at']
    list_filter = ['added_at']


User = get_user_model()


class UserAdminForm(DjangoUserAdmin.form):
    avatar = forms.ImageField(required=False, label="Avatar")

    class Meta(DjangoUserAdmin.form.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and hasattr(self.instance, 'profile') and self.instance.profile.avatar:
            self.fields['avatar'].initial = self.instance.profile.avatar

    def save(self, commit=True):
        user = super().save(commit)
        avatar = self.cleaned_data.get('avatar')
        if not hasattr(user, 'profile'):
            Profile.objects.get_or_create(user=user)
        profile = user.profile
        if avatar is False:
            # Clear existing avatar
            if profile.avatar:
                profile.avatar.delete(save=False)
                profile.avatar = ''
                profile.save(update_fields=['avatar'])
        elif avatar:
            profile.avatar = avatar
            profile.save()
        return user


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = UserAdminForm
    list_display = DjangoUserAdmin.list_display + ('avatar_preview',)
    list_select_related = ('profile',)
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Profile', {'fields': ('avatar',)}),
    )

    def avatar_preview(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit:cover;border-radius:50%;" />',
                obj.profile.avatar.url
            )
        return "—"
    avatar_preview.short_description = "Avatar"
