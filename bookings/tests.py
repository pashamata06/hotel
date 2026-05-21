from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    Client as HotelClient, RoomCategory, Room, Booking, 
    News, Employee, Vacancy, Review, PromoCode, DictionaryTerm, CompanyInfo
)

class ModelsTestCase(TestCase):
    def setUp(self):
        # Создаем тестовые данные
        self.category = RoomCategory.objects.create(
            name='Тестовая категория',
            comfort_level='standard',
            capacity=2,
            base_price=100.00
        )
        self.room = Room.objects.create(
            room_number='101',
            category=self.category,
            floor=1,
            is_active=True
        )
        self.news = News.objects.create(
            title='Тестовая новость',
            short_content='Краткое содержание',
            full_content='Полное содержание',
            is_published=True
        )
        self.vacancy = Vacancy.objects.create(
            title='Тестовая вакансия',
            description='Описание вакансии',
            is_active=True
        )
        self.review = Review.objects.create(
            user_name='Тестовый пользователь',
            rating=5,
            text='Отличный отель!',
            is_moderated=True
        )
        self.promo = PromoCode.objects.create(
            code='TEST123',
            discount_percent=10,
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            is_active=True
        )
        self.term = DictionaryTerm.objects.create(
            term='Тестовый термин',
            definition='Тестовое определение'
        )
        self.company = CompanyInfo.objects.create(
            name='Тестовая гостиница',
            founding_year=2020
        )

    def test_room_category_creation(self):
        self.assertEqual(self.category.name, 'Тестовая категория')
        self.assertEqual(self.category.base_price, 100.00)

    def test_room_creation(self):
        self.assertEqual(self.room.room_number, '101')
        self.assertEqual(self.room.category.name, 'Тестовая категория')

    def test_news_creation(self):
        self.assertEqual(self.news.title, 'Тестовая новость')
        self.assertTrue(self.news.is_published)

    def test_vacancy_creation(self):
        self.assertEqual(self.vacancy.title, 'Тестовая вакансия')
        self.assertTrue(self.vacancy.is_active)

    def test_review_creation(self):
        self.assertEqual(self.review.user_name, 'Тестовый пользователь')
        self.assertEqual(self.review.rating, 5)
        self.assertTrue(self.review.is_moderated)

    def test_promo_creation(self):
        self.assertEqual(self.promo.code, 'TEST123')
        self.assertEqual(self.promo.discount_percent, 10)

    def test_dictionary_term_creation(self):
        self.assertEqual(self.term.term, 'Тестовый термин')

    def test_company_info_creation(self):
        self.assertEqual(self.company.name, 'Тестовая гостиница')
        self.assertEqual(self.company.founding_year, 2020)

    def test_booking_price_calculation(self):
        client = HotelClient.objects.create(
            first_name='Иван',
            last_name='Тестов',
            birth_date=date(2000, 1, 1),
            phone='+375 (29) 111-11-11',
            email='test@test.com'
        )
        booking = Booking.objects.create(
            client=client,
            room=self.room,
            check_in_date=date(2026, 6, 1),
            check_out_date=date(2026, 6, 5)
        )
        expected_price = 100.00 * 4
        self.assertEqual(booking.total_price, expected_price)


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = RoomCategory.objects.create(
            name='Тест',
            comfort_level='standard',
            capacity=2,
            base_price=100.00
        )
        self.room = Room.objects.create(
            room_number='101',
            category=self.category,
            floor=1
        )
        self.news = News.objects.create(
            title='Новость',
            short_content='Кратко',
            full_content='Полностью',
            is_published=True
        )

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)

    def test_news_list_page(self):
        response = self.client.get('/news/')
        self.assertEqual(response.status_code, 200)

    def test_contacts_page(self):
        response = self.client.get('/contacts/')
        self.assertEqual(response.status_code, 200)

    def test_vacancies_page(self):
        response = self.client.get('/vacancies/')
        self.assertEqual(response.status_code, 200)

    def test_reviews_page(self):
        response = self.client.get('/reviews/')
        self.assertEqual(response.status_code, 200)

    def test_promocodes_page(self):
        response = self.client.get('/promocodes/')
        self.assertEqual(response.status_code, 200)

    def test_dictionary_page(self):
        response = self.client.get('/dictionary/')
        self.assertEqual(response.status_code, 200)

    def test_privacy_page(self):
        response = self.client.get('/privacy/')
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_review_create_post(self):
        response = self.client.post('/reviews/create/', {
            'name': 'Тест',
            'rating': 5,
            'text': 'Хороший отель'
        })
        self.assertEqual(response.status_code, 302)

    def test_search_news(self):
        response = self.client.get('/news/?search=Новость')
        self.assertEqual(response.status_code, 200)

    def test_api_weather_unauthorized(self):
        response = self.client.get('/api/weather/')
        self.assertEqual(response.status_code, 401)

    def test_api_exchange_unauthorized(self):
        response = self.client.get('/api/exchange/')
        self.assertEqual(response.status_code, 401)

    def test_api_weather_authorized(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/weather/')
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)

    def test_profile_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
