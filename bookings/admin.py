from django.contrib import admin
from .models import Client, RoomCategory, Room, Booking, Payment
from .models import News, Employee, Vacancy, Review, PromoCode, DictionaryTerm, CompanyInfo

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'phone', 'birth_date', 'created_at_utc']
    list_filter = ['has_child', 'birth_date']
    search_fields = ['last_name', 'first_name', 'phone', 'email']
    readonly_fields = ['created_at_utc']

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'comfort_level', 'capacity', 'base_price']
    list_filter = ['comfort_level']
    search_fields = ['name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'category', 'floor', 'is_active']
    list_filter = ['category', 'floor', 'is_active']
    search_fields = ['room_number']
    list_editable = ['is_active']

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 1

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'room', 'check_in_date', 'check_out_date', 'total_price']
    list_filter = ['check_in_date', 'check_out_date']
    search_fields = ['client__last_name', 'client__first_name', 'room__room_number']
    readonly_fields = ['total_price', 'created_at_utc']
    inlines = [PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'payment_date', 'method']
    list_filter = ['method', 'payment_date']
    readonly_fields = ['payment_date']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at_utc', 'is_published']
    list_filter = ['is_published', 'created_at_utc']
    search_fields = ['title']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'position', 'phone']
    list_filter = ['position']
    search_fields = ['last_name', 'first_name']

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at_utc']
    list_filter = ['is_active']
    search_fields = ['title']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'rating', 'created_at_utc', 'is_moderated']
    list_filter = ['rating', 'is_moderated', 'created_at_utc']
    search_fields = ['user_name', 'text']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'valid_from', 'valid_to', 'is_active']
    list_filter = ['is_active', 'valid_from', 'valid_to']
    search_fields = ['code']

@admin.register(DictionaryTerm)
class DictionaryTermAdmin(admin.ModelAdmin):
    list_display = ['term', 'added_at_utc']
    search_fields = ['term', 'definition']

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'founding_year']
