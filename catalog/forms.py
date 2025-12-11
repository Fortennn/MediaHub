from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Rating, MediaItem, Profile
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'input-auth'
            })


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логін або email'
        self.fields['username'].widget.attrs.update({
            'class': 'input-auth',
            'placeholder': 'Логін або email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'input-auth',
            'placeholder': 'Пароль'
        })

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            UserModel = get_user_model()
            try:
                user_obj = UserModel.objects.get(email__iexact=username)
                # Replace entered email with username so base auth works
                self.cleaned_data['username'] = user_obj.get_username()
            except UserModel.DoesNotExist:
                pass

        return super().clean()


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'form-control input-sakura',
                'min': 1,
                'max': 10,
                'step': 1
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control input-sakura',
                'rows': 4,
                'placeholder': 'Залиште ваш відгук...'
            })
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control input-sakura',
                'placeholder': 'Новий нікнейм'
            })
        }
        labels = {
            'username': 'Нікнейм'
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise ValidationError('Нікнейм не може бути порожнім.')
        # Ensure unique (case-insensitive)
        UserModel = get_user_model()
        existing = UserModel.objects.filter(username__iexact=username).exclude(pk=self.instance.pk)
        if existing.exists():
            raise ValidationError('Такий нікнейм вже використовується.')
        return username
