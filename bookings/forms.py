from django import forms
from .models import Review, Booking

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['user_name', 'rating', 'text']
        widgets = {
            'user_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'rating': forms.Select(attrs={'class': 'form-control'}, choices=[(i, str(i)) for i in range(1, 6)]),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ваш отзыв'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['client', 'room', 'check_in_date', 'check_out_date']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date'}),
        }
