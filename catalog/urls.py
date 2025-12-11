from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.media_list, name='media_list'),
    path('media/<int:pk>/', views.media_detail, name='media_detail'),
    path('media/<int:pk>/rate/', views.rate_media, name='rate_media'),
    path('media/<int:pk>/watchlist/', views.toggle_watchlist, name='toggle_watchlist'),
    path('ratings/<int:pk>/update/', views.update_rating, name='update_rating'),
    path('ratings/<int:pk>/delete/', views.delete_rating, name='delete_rating'),
    path('profile/', views.profile, name='profile'),
    path('watchlist/', views.user_watchlist, name='user_watchlist'),
    path('comments/', views.user_comments, name='user_comments'),
    path('search/', views.search, name='search'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True,
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
