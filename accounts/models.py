
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import re
from django.core.exceptions import ValidationError
from dms.common import DESIGNATION_CHOICES



class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email Address')
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255, verbose_name='Full Name')
    mobile = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False)
    is_it_dept = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    user_level = models.CharField(max_length=255, choices=DESIGNATION_CHOICES, null=True, blank=True)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    def clean(self):
        super().clean()
        errors = {}

        # Email validation
        if self.email:
            self.email = self.email.strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
                errors['email'] = _('Enter a valid email address.')

        # Username validation
        if self.username:
            self.username = self.username.strip()
            if len(self.username) < 4:
                errors['username'] = _('Username must be at least 4 characters.')
            if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
                errors['username'] = _('Username can only contain letters, numbers and underscores.')

        # Full name validation
        if self.full_name:
            self.full_name = ' '.join(self.full_name.strip().split())
            if len(self.full_name) < 3:
                errors['full_name'] = _('Full name must be at least 3 characters.')
            if len(self.full_name.split()) < 2:
                errors['full_name'] = _('Please provide both first and last name.')

        # Mobile validation
        if self.mobile and self.mobile.strip():
            self.mobile = self.mobile.strip()
            if not self.mobile.isdigit():
                errors['mobile'] = _('Mobile number should contain only digits.')
            if len(self.mobile) < 10:
                errors['mobile'] = _('Mobile number should be at least 10 digits.')
            if len(self.mobile) > 20:
                errors['mobile'] = _('Mobile number should not exceed 20 digits.')
        else:
            self.mobile = None

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_full_name(self):
        return self.full_name

    def __str__(self):
        return self.full_name + "-" + self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'