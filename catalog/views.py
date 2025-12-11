from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from .models import MediaItem, Genre, Rating, Watchlist, Profile
from .forms import CustomUserCreationForm, RatingForm, ProfileForm

def _matches_media_item(item, query_cf):
    """Case-insensitive (Unicode) match across title/original_title/description using Python casefold."""
    fields = [item.title, item.original_title, item.description]
    return any(query_cf in (value or '').casefold() for value in fields)

def home(request):
    latest_movies = MediaItem.objects.filter(
        media_type='movie',
        is_published=True
    ).order_by('-created_at')[:4]
    
    latest_series = MediaItem.objects.filter(
        media_type='series',
        is_published=True
    ).order_by('-created_at')[:4]
    
    latest_anime = MediaItem.objects.filter(
        media_type='anime',
        is_published=True
    ).order_by('-created_at')[:4]
    
    from django.db.models import Count
    movie_count = MediaItem.objects.filter(media_type='movie', is_published=True).count()
    series_count = MediaItem.objects.filter(media_type='series', is_published=True).count()
    anime_count = MediaItem.objects.filter(media_type='anime', is_published=True).count()
    rating_count = Rating.objects.count()
    
    context = {
        'latest_movies': latest_movies,
        'latest_series': latest_series,
        'latest_anime': latest_anime,
        'movie_count': movie_count,
        'series_count': series_count,
        'anime_count': anime_count,
        'rating_count': rating_count,
    }
    return render(request, 'catalog/home.html', context)

def media_list(request):
    media_type = request.GET.get('type', 'all')
    genre_slug = request.GET.get('genre')
    sort_by = request.GET.get('sort', '-created_at')
    
    items = MediaItem.objects.filter(is_published=True)
    
    all_count = items.count()
    movie_count = items.filter(media_type='movie').count()
    series_count = items.filter(media_type='series').count()
    anime_count = items.filter(media_type='anime').count()
    
    if media_type != 'all':
        items = items.filter(media_type=media_type)
    
    if genre_slug:
        items = items.filter(genres__slug=genre_slug)
    
    items = items.annotate(
        avg_rating=Avg('ratings__score')
    )
    
    valid_sorts = ['-created_at', 'title', '-release_year', '-avg_rating']
    if sort_by in valid_sorts:
        items = items.order_by(sort_by)
    
    genres = Genre.objects.all()
    
    paginator = Paginator(items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'genres': genres,
        'current_type': media_type,
        'current_genre': genre_slug,
        'current_sort': sort_by,
        'all_count': all_count,
        'movie_count': movie_count,
        'series_count': series_count,
        'anime_count': anime_count,
    }
    return render(request, 'catalog/media_list.html', context)

def media_detail(request, pk):
    media = get_object_or_404(MediaItem, pk=pk, is_published=True)
    user_rating = None
    
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(
            user=request.user, 
            media_item=media
        ).first()
        
        watchlist_item = Watchlist.objects.filter(
            user=request.user,
            media_item=media
        ).first()
        is_in_watchlist = bool(watchlist_item)
        watchlist_status = watchlist_item.status if watchlist_item else Watchlist.Status.PLANNED
    else:
        is_in_watchlist = False
        watchlist_status = Watchlist.Status.PLANNED
    
    ratings = media.ratings.select_related('user').order_by('-created_at')
    seasons = media.seasons.all()
    season_count = seasons.count()
    episode_count = seasons.aggregate(total_episodes=Sum('episodes_count')).get('total_episodes') or 0
    
    context = {
        'media': media,
        'seasons': seasons,
        'season_count': season_count,
        'episode_count': episode_count,
        'user_rating': user_rating,
        'is_in_watchlist': is_in_watchlist,
        'watchlist_status': watchlist_status,
        'ratings': ratings,
    }
    return render(request, 'catalog/media_detail.html', context)

@login_required
def rate_media(request, pk):
    media = get_object_or_404(MediaItem, pk=pk)
    
    if request.method == 'POST':
        score = request.POST.get('score')
        comment = request.POST.get('comment', '')
        
        Rating.objects.update_or_create(
            user=request.user,
            media_item=media,
            defaults={'score': score, 'comment': comment}
        )
    
    return redirect('media_detail', pk=pk)


def _safe_redirect(request, fallback_url):
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return fallback_url


@login_required
def update_rating(request, pk):
    rating = get_object_or_404(Rating, pk=pk, user=request.user)
    fallback_url = reverse('media_detail', args=[rating.media_item.pk])
    redirect_url = _safe_redirect(request, fallback_url)

    if request.method == 'POST':
        score = request.POST.get('score')
        comment = request.POST.get('comment', '')

        if score:
            rating.score = int(score)
            rating.comment = comment
            rating.save()
            messages.success(request, 'Відгук оновлено.')

    return redirect(redirect_url)


@login_required
def delete_rating(request, pk):
    rating = get_object_or_404(Rating, pk=pk, user=request.user)
    fallback_url = reverse('media_detail', args=[rating.media_item.pk])
    redirect_url = _safe_redirect(request, fallback_url)

    if request.method == 'POST':
        rating.delete()
        messages.success(request, 'Коментар видалено.')

    return redirect(redirect_url)

@login_required
def toggle_watchlist(request, pk):
    media = get_object_or_404(MediaItem, pk=pk)
    redirect_url = _safe_redirect(request, reverse('media_detail', args=[pk]))
    
    if request.method == 'POST':
        status = request.POST.get('status', Watchlist.Status.PLANNED)
        remove = request.POST.get('remove')

        if remove:
            watchlist_item = Watchlist.objects.filter(user=request.user, media_item=media).first()
            if watchlist_item:
                watchlist_item.delete()
                messages.success(request, 'Видалено зі списку перегляду.')
        else:
            watchlist_item, created = Watchlist.objects.get_or_create(
                user=request.user,
                media_item=media,
                defaults={'status': status}
            )

            if watchlist_item.status != status:
                watchlist_item.status = status
                watchlist_item.save(update_fields=['status'])
                messages.success(request, 'Статус у списку перегляду оновлено.')
            elif created:
                messages.success(request, 'Додано до списку перегляду.')

    return redirect(redirect_url)

@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аватар оновлено.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj)

    watchlist_items = Watchlist.objects.filter(
        user=request.user
    ).select_related('media_item')
    
    ratings = Rating.objects.filter(
        user=request.user
    ).select_related('media_item')
    
    context = {
        'watchlist_count': watchlist_items.count(),
        'rating_count': ratings.count(),
        'latest_watchlist': watchlist_items[:5],
        'recent_ratings': ratings[:5],
        'profile': profile_obj,
        'profile_form': form,
    }
    
    return render(request, 'catalog/profile.html', context)

@login_required
def user_comments(request):
    comments = Rating.objects.filter(
        user=request.user
    ).exclude(
        comment__isnull=True
    ).exclude(
        comment__exact=''
    ).select_related('media_item').order_by('-created_at')

    return render(request, 'catalog/user_comments.html', {
        'comments': comments,
    })

@login_required
def user_watchlist(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all')
    media_type_filter = request.GET.get('type', 'all')
    base_watchlist = Watchlist.objects.filter(
        user=request.user
    ).select_related('media_item').order_by('-added_at')

    status_counts = {
        value: base_watchlist.filter(status=value).count()
        for value, label in Watchlist.Status.choices
    }

    status_tabs = [
        {
            'value': value,
            'label': label,
            'count': status_counts.get(value, 0)
        }
        for value, label in Watchlist.Status.choices
    ]

    filtered_watchlist = base_watchlist

    valid_media_types = {'movie', 'series', 'anime'}
    if media_type_filter in valid_media_types:
        filtered_watchlist = filtered_watchlist.filter(media_item__media_type=media_type_filter)
    else:
        media_type_filter = 'all'

    valid_statuses = {choice[0] for choice in Watchlist.Status.choices}
    if status_filter in valid_statuses:
        filtered_watchlist = filtered_watchlist.filter(status=status_filter)
    else:
        status_filter = 'all'

    filtered_watchlist_list = list(filtered_watchlist)

    if search_query:
        query_cf = search_query.casefold()
        filtered_watchlist_list = [
            item for item in filtered_watchlist_list
            if _matches_media_item(item.media_item, query_cf)
        ]

    total_watchlist_count = len(filtered_watchlist_list)

    return render(request, 'catalog/watchlist.html', {
        'watchlist': filtered_watchlist_list,
        'search_query': search_query,
        'status_filter': status_filter,
        'media_type_filter': media_type_filter,
        'status_tabs': status_tabs,
        'total_watchlist_count': total_watchlist_count,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        query_cf = query.casefold()
        base_items = MediaItem.objects.filter(is_published=True).select_related().prefetch_related('genres').order_by('-created_at')
        results = [item for item in base_items if _matches_media_item(item, query_cf)]
    
    return render(request, 'catalog/search.html', {
        'query': query,
        'results': results
    })

def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    suggestions = []

    if query:
        query_cf = query.casefold()
        base_qs = (
            MediaItem.objects.filter(is_published=True)
            .annotate(avg_rating=Avg('ratings__score'))
            .order_by('-created_at')
        )[:50]

        matches = [
            item for item in base_qs
            if _matches_media_item(item, query_cf)
        ][:8]

        suggestions = [
            {
                'id': item.pk,
                'title': item.title,
                'type': item.media_type,
                'type_label': item.get_media_type_display(),
                'release_year': item.release_year,
                'avg_rating': item.avg_rating or 0,
                'url': reverse('media_detail', args=[item.pk]),
                'poster': item.poster.url if item.poster else None,
            }
            for item in matches
        ]

    return JsonResponse({'results': suggestions})



from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        
        if password1 != password2:
            messages.error(request, 'Паролі не співпадають')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Користувач з таким іменем вже існує')
            return redirect('register')
        
        try:
            user = User.objects.create_user(username=username, password=password1, email=email)
            user.save()
            
            user = authenticate(username=username, password=password1)
            if user is not None:
                login(request, user)
                messages.success(request, 'Вітаємо! Ви успішно зареєструвалися.')
                return redirect('home')
        except Exception as e:
            messages.error(request, f'Помилка при реєстрації: {str(e)}')
            return redirect('register')
    
    return render(request, 'registration/register.html')

def media_list(request):
    media_type = request.GET.get('type', 'all')
    genre_slug = request.GET.get('genre')
    sort_by = request.GET.get('sort', '-created_at')
    search_query = request.GET.get('q', '').strip()
    
    items = MediaItem.objects.filter(is_published=True)
    
    if media_type != 'all':
        items = items.filter(media_type=media_type)
    
    if genre_slug:
        items = items.filter(genres__slug=genre_slug)
    
    items = items.annotate(
        avg_rating=Avg('ratings__score'),
        rating_count=Count('ratings')
    ).distinct()
    
    movie_count = MediaItem.objects.filter(media_type='movie', is_published=True).count()
    series_count = MediaItem.objects.filter(media_type='series', is_published=True).count()
    anime_count = MediaItem.objects.filter(media_type='anime', is_published=True).count()
    
    valid_sorts = ['-created_at', 'title', '-release_year', '-avg_rating']
    if sort_by in valid_sorts:
        items = items.order_by(sort_by)
    
    if search_query:
        query_cf = search_query.casefold()
        items_list = [item for item in items if _matches_media_item(item, query_cf)]
    else:
        items_list = list(items)
    
    genres = Genre.objects.all()
    
    user_watchlist = []
    if request.user.is_authenticated:
        user_watchlist = Watchlist.objects.filter(
            user=request.user
        ).values_list('media_item_id', flat=True)

    paginator = Paginator(items_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'genres': genres,
        'current_type': media_type,
        'current_genre': genre_slug,
        'current_sort': sort_by,
        'movie_count': movie_count,
        'series_count': series_count,
        'anime_count': anime_count,
        'user_watchlist': user_watchlist,
    }
    return render(request, 'catalog/media_list.html', context)
