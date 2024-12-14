# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserChangeForm, SetPasswordForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProfile


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label='Konfirmasi Password'
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Password'
    )


class UserProfileForm(forms.ModelForm):
    phone_number = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Enter a valid phone number.'
            )
        ],
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'gender',
            'birth_date',
            'phone_number',
            'education_level',
            'occupation',
            'profile_image'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Cek apakah email sudah digunakan oleh user lain
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Email sudah digunakan')
        return email


class PasswordChangeForm(SetPasswordForm):
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('Konfirmasi password tidak cocok.')

        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError('Email tidak terdaftar atau tidak aktif')
        return email


class AccountDeleteForm(forms.Form):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label='Konfirmasi Password'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get('confirm_password')

        if not self.user.check_password(confirm_password):
            raise forms.ValidationError('Password salah')

        return confirm_password