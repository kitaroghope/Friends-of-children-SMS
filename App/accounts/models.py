"""
Custom User model for the SMS system.
Supports multiple user types: Staff, Parent, or both.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings


class UserManager(BaseUserManager):
    """Custom user manager for the User model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for the SMS system.
    Uses email as the primary identifier instead of username.
    Supports being a Staff member, Parent, or both.
    """

    USER_TYPE_CHOICES = [
        ('staff', 'Staff'),
        ('parent', 'Parent'),
        ('both', 'Both Staff and Parent'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='staff'
    )
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Override username field to make it nullable (we use email as identifier)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ['email']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def is_staff_member(self):
        """Check if user is a staff member."""
        return self.user_type in ('staff', 'both')

    def is_parent(self):
        """Check if user is a parent."""
        return self.user_type in ('parent', 'both')
