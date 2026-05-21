from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('dictionary/', views.dictionary, name='dictionary'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews, name='reviews'),
    path('reviews/create/', views.review_create, name='review_create'),
    path('promocodes/', views.promocodes, name='promocodes'),
    path('profile/', views.profile, name='profile'),
]

# API endpoints (требуют авторизацию)
urlpatterns += [
    path('api/weather/', views.api_weather, name='api_weather'),
    path('api/exchange/', views.api_exchange, name='api_exchange'),
]

# CRUD для отзывов
urlpatterns += [
    path('reviews/update/<int:pk>/', views.review_update, name='review_update'),
    path('reviews/delete/<int:pk>/', views.review_delete, name='review_delete'),
]

# CRUD для броней
urlpatterns += [
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/create/', views.booking_create, name='booking_create'),
    path('bookings/update/<int:pk>/', views.booking_update, name='booking_update'),
    path('bookings/delete/<int:pk>/', views.booking_delete, name='booking_delete'),
]
