from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

def validate_age_18(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError('Возраст должен быть 18 лет и старше')

class Client(models.Model):
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    patronymic = models.CharField('Отчество', max_length=50, blank=True)
    birth_date = models.DateField('Дата рождения', validators=[validate_age_18])
    phone = models.CharField('Телефон', max_length=20, validators=[RegexValidator(r'^\+375 \(29\) \d{3}-\d{2}-\d{2}$', 'Формат: +375 (29) XXX-XX-XX')])
    email = models.EmailField('Email')
    created_at_utc = models.DateTimeField('Дата создания (UTC)', default=timezone.now)
    created_at_local = models.DateTimeField('Дата создания (локальная)', blank=True, null=True)
    has_child = models.BooleanField('Есть ли ребенок', default=False)
    
    def __str__(self):
        return f'{self.last_name} {self.first_name}'
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class RoomCategory(models.Model):
    COMFORT_CHOICES = [
        ('economy', 'Эконом'),
        ('standard', 'Стандарт'),
        ('superior', 'Улучшенный'),
        ('lux', 'Люкс'),
        ('president', 'Президентский'),
    ]
    
    name = models.CharField('Название категории', max_length=50)
    comfort_level = models.CharField('Комфортность', max_length=20, choices=COMFORT_CHOICES)
    capacity = models.PositiveIntegerField('Вместимость (чел)', validators=[MinValueValidator(1), MaxValueValidator(10)])
    base_price = models.DecimalField('Базовая цена за ночь', max_digits=10, decimal_places=2)
    description = models.TextField('Описание', blank=True)
    
    def __str__(self):
        return f'{self.name} ({self.get_comfort_level_display()})'
    
    class Meta:
        verbose_name = 'Категория номера'
        verbose_name_plural = 'Категории номеров'

class Room(models.Model):
    room_number = models.CharField('Номер комнаты', max_length=10, unique=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='rooms', verbose_name='Категория')
    floor = models.PositiveIntegerField('Этаж')
    has_window = models.BooleanField('Окно', default=True)
    photo = models.ImageField('Фото', upload_to='rooms/', blank=True, null=True)
    is_active = models.BooleanField('Активен', default=True)
    
    def __str__(self):
        return f'Номер {self.room_number} - {self.category.name}'
    
    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'

class Booking(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings', verbose_name='Клиент')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', verbose_name='Номер')
    check_in_date = models.DateField('Дата заезда')
    check_out_date = models.DateField('Дата выезда')
    total_price = models.DecimalField('Итоговая цена', max_digits=10, decimal_places=2, blank=True)
    created_at_utc = models.DateTimeField('Дата создания (UTC)', default=timezone.now)
    
    def save(self, *args, **kwargs):
        days = (self.check_out_date - self.check_in_date).days
        if days > 0:
            self.total_price = self.room.category.base_price * days
        else:
            self.total_price = self.room.category.base_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Бронь {self.client} - {self.room} ({self.check_in_date})'
    
    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('online', 'Онлайн'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment', verbose_name='Бронь')
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField('Дата оплаты', default=timezone.now)
    method = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_METHODS)
    
    def __str__(self):
        return f'Оплата {self.amount} по брони #{self.booking.id}'
    
    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'

class News(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    short_content = models.CharField('Краткое содержание', max_length=500)
    full_content = models.TextField('Полное содержание')
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    created_at_utc = models.DateTimeField('Дата создания (UTC)', default=timezone.now)
    is_published = models.BooleanField('Опубликовано', default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at_utc']

class Employee(models.Model):
    POSITION_CHOICES = [
        ('manager', 'Менеджер'),
        ('reception', 'Администратор'),
        ('housekeeping', 'Горничная'),
        ('maintenance', 'Технический персонал'),
    ]
    
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    position = models.CharField('Должность', max_length=50, choices=POSITION_CHOICES)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    photo = models.ImageField('Фото', upload_to='employees/', blank=True, null=True)
    work_description = models.TextField('Описание работ', blank=True)
    birth_date = models.DateField('Дата рождения', validators=[validate_age_18])
    
    def __str__(self):
        return f'{self.last_name} {self.first_name} - {self.get_position_display()}'
    
    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

class Vacancy(models.Model):
    title = models.CharField('Название вакансии', max_length=200)
    description = models.TextField('Описание')
    salary_min = models.DecimalField('Мин. зарплата', max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField('Макс. зарплата', max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at_utc = models.DateTimeField('Дата создания', default=timezone.now)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='reviews', verbose_name='Пользователь', null=True, blank=True)
    user_name = models.CharField('Имя пользователя', max_length=100)
    rating = models.IntegerField('Оценка', choices=RATING_CHOICES)
    text = models.TextField('Текст отзыва')
    created_at_utc = models.DateTimeField('Дата создания (UTC)', default=timezone.now)
    is_moderated = models.BooleanField('Опубликован', default=True)
    
    def __str__(self):
        return f'{self.user_name} - {self.rating}★'
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at_utc']

class PromoCode(models.Model):
    code = models.CharField('Код', max_length=50, unique=True)
    discount_percent = models.IntegerField('Скидка %', validators=[MinValueValidator(0), MaxValueValidator(100)])
    description = models.TextField('Описание', blank=True)
    valid_from = models.DateField('Действует с')
    valid_to = models.DateField('Действует по')
    is_active = models.BooleanField('Активен', default=True)
    created_at_utc = models.DateTimeField('Дата создания', default=timezone.now)
    
    def __str__(self):
        status = '✅' if self.is_active and self.valid_to >= date.today() else '📦'
        return f'{status} {self.code} - {self.discount_percent}%'
    
    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'

class DictionaryTerm(models.Model):
    term = models.CharField('Термин', max_length=200, unique=True)
    definition = models.TextField('Определение')
    added_at_utc = models.DateTimeField('Дата добавления (UTC)', default=timezone.now)
    
    def __str__(self):
        return self.term
    
    class Meta:
        verbose_name = 'Термин'
        verbose_name_plural = 'Термины'
        ordering = ['term']

class CompanyInfo(models.Model):
    name = models.CharField('Название', max_length=200, default='Гостиница "Уют"')
    founding_year = models.IntegerField('Год основания', null=True, blank=True)
    legal_address = models.TextField('Юридический адрес', blank=True)
    inn = models.CharField('ИНН', max_length=20, blank=True)
    kpp = models.CharField('КПП', max_length=20, blank=True)
    bank_account = models.CharField('Расчетный счет', max_length=30, blank=True)
    bank_name = models.CharField('Банк', max_length=200, blank=True)
    bik = models.CharField('БИК', max_length=20, blank=True)
    history_text = models.TextField('История компании', blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'
