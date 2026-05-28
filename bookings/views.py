from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .models import News, Employee, Vacancy, Review, PromoCode, DictionaryTerm, CompanyInfo, Room, RoomCategory, Booking, Client
import calendar
from datetime import datetime, date, timedelta
import pytz
import urllib.request
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import logging
from functools import wraps

logger = logging.getLogger('bookings')

def api_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized. Please login.'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

def get_user_timezone(request):
    return request.session.get('user_timezone', 'Europe/Minsk')

def get_calendar():
    now = datetime.now()
    cal = calendar.monthcalendar(now.year, now.month)
    html = '<table class="calendar"><td><th>Пн</th><th>Вт</th><th>Ср</th><th>Чт</th><th>Пт</th><th>Сб</th><th>Вс</th></tr>'
    for week in cal:
        html += '<tr>'
        for day in week:
            if day == 0:
                html += '<td>   </td>'
            else:
                html += f'<td>{day}</td>'
        html += '</tr>'
    html += '</table>'
    return html

def base_context(request):
    tz = get_user_timezone(request)
    now_local = datetime.now(pytz.timezone(tz))
    return {
        'current_date': now_local,
        'user_timezone': tz,
        'utc_time': timezone.now(),
        'calendar': get_calendar(),
    }

def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=53.9&longitude=27.5667&current_weather=true"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            weather = data.get('current_weather', {})
            return {
                'temperature': weather.get('temperature', 'Н/Д'),
                'wind_speed': weather.get('windspeed', 'Н/Д'),
            }
    except:
        return {'temperature': 'Н/Д', 'wind_speed': 'Н/Д', 'error': True}

def get_exchange_rate():
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            usd_rate = 3.20
            eur_rate = 3.10
            for item in data:
                if item.get('Cur_Abbreviation') == 'USD':
                    usd_rate = item.get('Cur_OfficialRate', 3.20)
                if item.get('Cur_Abbreviation') == 'EUR':
                    eur_rate = item.get('Cur_OfficialRate', 3.10)
            return {
                'usd_to_byn': round(usd_rate, 2),
                'eur_to_byn': round(eur_rate, 2)
            }
    except:
        return {'usd_to_byn': 3.20, 'eur_to_byn': 3.10, 'error': True}

def get_booking_chart():
    try:
        months_data = [
            ('Май 2026', 5, 2026),
            ('Июнь 2026', 6, 2026),
            ('Июль 2026', 7, 2026),
            ('Август 2026', 8, 2026),
            ('Сентябрь 2026', 9, 2026),
        ]
        
        months = []
        bookings_count = []
        
        for month_name, month_num, year in months_data:
            month_start = date(year, month_num, 1)
            if month_num == 12:
                month_end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(year, month_num + 1, 1) - timedelta(days=1)
            
            count = Booking.objects.filter(
                check_in_date__lte=month_end,
                check_out_date__gte=month_start
            ).count()
            
            months.append(month_name)
            bookings_count.append(count)
        
        plt.figure(figsize=(10, 5))
        bars = plt.bar(months, bookings_count, color='#3498db', edgecolor='black')
        
        for bar, count in zip(bars, bookings_count):
            if count > 0:
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        str(count), ha='center', va='bottom', fontsize=10)
        
        plt.title('Загрузка гостиницы по месяцам', fontsize=14, fontweight='bold')
        plt.xlabel('Месяц', fontsize=12)
        plt.ylabel('Количество броней', fontsize=12)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f'data:image/png;base64,{image_base64}'
    except Exception as e:
        logger.error(f"Ошибка графика: {e}")
        return None

@api_login_required
def api_weather(request):
    return JsonResponse(get_weather())

@api_login_required
def api_exchange(request):
    return JsonResponse(get_exchange_rate())

def home(request):
    context = base_context(request)
    context['latest_news'] = News.objects.filter(is_published=True).first()
    context['popular_rooms'] = Room.objects.filter(is_active=True)[:3]
    context['weather'] = get_weather()
    context['exchange_rates'] = get_exchange_rate()
    context['booking_chart'] = get_booking_chart()
    return render(request, 'bookings/home.html', context)

def about(request):
    context = base_context(request)
    context['company'] = CompanyInfo.objects.first()
    return render(request, 'bookings/about.html', context)

def news_list(request):
    context = base_context(request)
    queryset = News.objects.filter(is_published=True)
    
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(short_content__icontains=search_query) |
            Q(full_content__icontains=search_query)
        )
        context['search_query'] = search_query
    
    sort_by = request.GET.get('sort', '-created_at_utc')
    allowed_sorts = ['title', '-title', 'created_at_utc', '-created_at_utc']
    if sort_by in allowed_sorts:
        queryset = queryset.order_by(sort_by)
        context['sort_by'] = sort_by
    
    context['news_list'] = queryset
    return render(request, 'bookings/news_list.html', context)

def news_detail(request, pk):
    context = base_context(request)
    context['news'] = get_object_or_404(News, pk=pk, is_published=True)
    return render(request, 'bookings/news_detail.html', context)

def dictionary(request):
    context = base_context(request)
    sort_by = request.GET.get('sort', 'term')
    if sort_by == '-term':
        context['terms'] = DictionaryTerm.objects.all().order_by('-term')
    else:
        context['terms'] = DictionaryTerm.objects.all().order_by('term')
    context['sort_by'] = sort_by
    
    search_query = request.GET.get('search', '')
    if search_query:
        context['terms'] = context['terms'].filter(
            Q(term__icontains=search_query) |
            Q(definition__icontains=search_query)
        )
        context['search_query'] = search_query
    
    return render(request, 'bookings/dictionary.html', context)

def contacts(request):
    context = base_context(request)
    context['employees'] = Employee.objects.all()
    return render(request, 'bookings/contacts.html', context)

def privacy(request):
    context = base_context(request)
    return render(request, 'bookings/privacy.html', context)

def vacancies(request):
    context = base_context(request)
    queryset = Vacancy.objects.filter(is_active=True)
    
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        context['search_query'] = search_query
    
    sort_by = request.GET.get('sort', '-created_at_utc')
    if sort_by == 'salary':
        queryset = queryset.order_by('salary_min')
    elif sort_by == '-salary':
        queryset = queryset.order_by('-salary_min')
    else:
        queryset = queryset.order_by(sort_by)
    
    context['vacancies'] = queryset
    context['sort_by'] = sort_by
    return render(request, 'bookings/vacancies.html', context)

def reviews(request):
    context = base_context(request)
    context['reviews'] = Review.objects.filter(is_moderated=True)
    return render(request, 'bookings/reviews.html', context)

def review_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        rating = request.POST.get('rating')
        text = request.POST.get('text')
        if name and rating and text:
            Review.objects.create(
                user_name=name,
                rating=int(rating),
                text=text,
                is_moderated=True
            )
            logger.info(f"Новый отзыв от {name}, оценка {rating}")
            messages.success(request, 'Спасибо за отзыв!')
            return redirect('bookings:reviews')
    context = base_context(request)
    return render(request, 'bookings/review_form.html', context)

@login_required
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    # Только автор или админ может редактировать
    if review.user != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы можете редактировать только свои отзывы')
        return redirect('bookings:reviews')
    
    if request.method == 'POST':
        from .forms import ReviewForm
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв обновлён!')
            return redirect('bookings:reviews')
    else:
        from .forms import ReviewForm
        form = ReviewForm(instance=review)
    
    context = base_context(request)
    context['form'] = form
    context['review'] = review
    context['is_edit'] = True
    return render(request, 'bookings/review_form.html', context)

@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    # Только автор или админ может удалить
    if review.user != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы можете удалять только свои отзывы')
        return redirect('bookings:reviews')
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удалён!')
        return redirect('bookings:reviews')
    
    context = base_context(request)
    context['review'] = review
    return render(request, 'bookings/review_confirm_delete.html', context)

@login_required
def booking_list(request):
    context = base_context(request)
    if request.user.is_superuser:
        context['bookings'] = Booking.objects.all().order_by('-check_in_date')
    else:
        context['bookings'] = Booking.objects.filter(client__email=request.user.email).order_by('-check_in_date')
    return render(request, 'bookings/booking_list.html', context)

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # Проверка доступа: админ или владелец
    if not request.user.is_superuser and booking.client.email != request.user.email:
        messages.error(request, 'У вас нет доступа к этой брони')
        return redirect('bookings:booking_list')
    context = base_context(request)
    context['booking'] = booking
    return render(request, 'bookings/booking_detail.html', context)

@login_required
def booking_create(request):
    if request.method == 'POST':
        from .forms import BookingForm
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            messages.success(request, 'Бронь создана!')
            return redirect('bookings:booking_detail', pk=booking.pk)
    else:
        from .forms import BookingForm
        form = BookingForm()
    
    context = base_context(request)
    context['form'] = form
    context['is_edit'] = False
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # Проверка доступа: админ или владелец
    if not request.user.is_superuser and booking.client.email != request.user.email:
        messages.error(request, 'Вы можете редактировать только свои брони')
        return redirect('bookings:booking_list')
    
    if request.method == 'POST':
        from .forms import BookingForm
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Бронь обновлена!')
            return redirect('bookings:booking_detail', pk=booking.pk)
    else:
        from .forms import BookingForm
        form = BookingForm(instance=booking)
    
    context = base_context(request)
    context['form'] = form
    context['booking'] = booking
    context['is_edit'] = True
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # Проверка доступа: админ или владелец
    if not request.user.is_superuser and booking.client.email != request.user.email:
        messages.error(request, 'Вы можете удалять только свои брони')
        return redirect('bookings:booking_list')
    
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Бронь удалена!')
        return redirect('bookings:booking_list')
    
    context = base_context(request)
    context['booking'] = booking
    return render(request, 'bookings/booking_confirm_delete.html', context)

def promocodes(request):
    context = base_context(request)
    today = date.today()
    context['active_promocodes'] = PromoCode.objects.filter(is_active=True, valid_from__lte=today, valid_to__gte=today)
    context['archive_promocodes'] = PromoCode.objects.filter(is_active=False) | PromoCode.objects.filter(valid_to__lt=today)
    return render(request, 'bookings/promocodes.html', context)

@login_required
def profile(request):
    context = base_context(request)
    context['user_bookings'] = Booking.objects.filter(client__email=request.user.email)[:10]
    return render(request, 'bookings/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserCreationForm()
    context = base_context(request)
    context['form'] = form
    return render(request, 'registration/register.html', context)
