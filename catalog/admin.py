from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, MediaItem, Season, Rating, Watchlist


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
