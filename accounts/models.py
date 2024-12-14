# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.core.validators import EmailValidator, RegexValidator, FileExtensionValidator
from django.conf import settings

import uuid
import os

def user_profile_image_path(instance, filename):
    """
    Generate path untuk foto profil
    """
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('profile_images', str(instance.user.id), filename)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Model Pengguna Kustom dengan Fitur Tambahan
    """
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('id', 'Bahasa Indonesia'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        validators=[EmailValidator()]
    )
    username = models.CharField(
        _('username'),
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. Use letters, numbers, and @/./+/-/_ only.')
            )
        ]
    )

    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=True
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user account should be treated as active.')
    )
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether the user has verified their email.')
    )

    two_factor_enabled = models.BooleanField(
        _('two-factor authentication'),
        default=False
    )

    login_count = models.PositiveIntegerField(
        _('login count'),
        default=0
    )
    last_login_ip = models.GenericIPAddressField(
        _('last login IP'),
        null=True,
        blank=True
    )

    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )
    last_activity = models.DateTimeField(
        _('last activity'),
        null=True,
        blank=True
    )

    language_preference = models.CharField(
        _('language preference'),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en'
    )

    objects = settings.AUTH_USER_MODEL

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'username']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email

    def get_short_name(self):
        return self.first_name or self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

class UserProfile(models.Model):
    """
    Model profil tambahan untuk pengguna
    """
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
        ('N', _('Prefer not to say'))
    ]

    EDUCATION_LEVELS = [
        ('SD', _('Elementary School')),
        ('SMP', _('Junior High School')),
        ('SMA', _('Senior High School')),
        ('D3', _('Diploma')),
        ('S1', _('Bachelor')),
        ('S2', _('Master')),
        ('S3', _('Doctorate')),
        ('OTHER', _('Other'))
    ]

    MARITAL_STATUS_CHOICES = [
        ('S', _('Single')),
        ('M', _('Married')),
        ('D', _('Divorced')),
        ('W', _('Widowed'))
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )

    gender = models.CharField(
        _('Gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    birth_date = models.DateField(
        _('Birth Date'),
        null=True,
        blank=True
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        _('Phone Number'),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )

    education_level = models.CharField(
        _('Education Level'),
        max_length=10,
        choices=EDUCATION_LEVELS,
        blank=True
    )

    occupation = models.CharField(
        _('Occupation'),
        max_length=100,
        blank=True
    )

    marital_status = models.CharField(
        _('Marital Status'),
        max_length=1,
        choices=MARITAL_STATUS_CHOICES,
        blank=True
    )

    profile_image = models.ImageField(
        _('Profile Image'),
        upload_to=user_profile_image_path,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        null=True,
        blank=True,
        max_length=255
    )

    address = models.TextField(
        _('Address'),
        blank=True,
        null=True
    )

    city = models.CharField(
        _('City'),
        max_length=100,
        blank=True
    )

    country = models.CharField(
        _('Country'),
        max_length=100,
        blank=True
    )

    postal_code = models.CharField(
        _('Postal Code'),
        max_length=20,
        blank=True
    )

    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        ordering = ['-created_at']

class UserActivity(models.Model):
    """
    Model untuk melacak aktivitas pengguna
    """
    ACTIVITY_TYPES = [
        ('LOGIN', _('Login')),
        ('LOGOUT', _('Logout')),
        ('REGISTRATION', _('Registration')),
        ('PROFILE_UPDATE', _('Profile Update')),
        ('PASSWORD_CHANGE', _('Password Change')),
        ('EMAIL_VERIFICATION', _('Email Verification')),
        ('ACCOUNT_ACTIVATION', _('Account Activation')),
        ('TWO_FACTOR_AUTH', _('Two-Factor Authentication')),
        ('PASSWORD_RESET', _('Password Reset')),
        ('DEVICE_LOGIN', _('Device Login')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('User ')
    )

    activity_type = models.CharField(
        _('Activity Type'),
        max_length=30,
        choices=ACTIVITY_TYPES
    )

    ip_address = models.GenericIPAddressField(
        _('IP Address'),
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        _('User  Agent'),
        blank=True,
        null=True
    )

    location = models.CharField(
        _('Location'),
        max_length=255,
        blank=True,
        null=True
    )

    timestamp = models.DateTimeField(
        _('Timestamp'),
        auto_now_add=True
    )

    additional_info = models.JSONField(
        _('Additional Information'),
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

    @classmethod
    def log_activity(
            cls,
            user,
            activity_type,
            ip_address=None,
            user_agent=None,
            location=None,
            additional_info=None
    ):
        """
        Metode kelas untuk mencatat aktivitas dengan mudah
        """
        return cls.objects.create(
            user=user,
            activity_type=activity_type,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            additional_info=additional_info
        )

    class Meta:
        verbose_name = _('User  Activity')
        verbose_name_plural = _('User  Activities')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type', 'timestamp']),
        ]