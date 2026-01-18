"""
Serializers for Accounts app.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone',
            'user_type', 'is_active', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['last_login', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create user with hashed password."""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user with password handling."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user self-registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class SchoolRequestSerializer(serializers.ModelSerializer):
    """Serializer for school registration requests."""

    class Meta:
        from core.models import SchoolRequest
        model = SchoolRequest
        fields = [
            'id', 'status', 'requester_name', 'requester_email', 'requester_phone',
            'school_name', 'school_acronym', 'school_phone', 'school_email',
            'school_address', 'currency', 'notes',
            'reviewed_by', 'reviewed_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'status', 'reviewed_by', 'reviewed_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]


class SchoolOnboardingSerializer(serializers.Serializer):
    """Serializer for creating a school with owner from an approved request."""
    request_id = serializers.IntegerField()

    def validate_request_id(self, value):
        from core.models import SchoolRequest
        try:
            request = SchoolRequest.objects.get(id=value, status='approved')
        except SchoolRequest.DoesNotExist:
            raise serializers.ValidationError(
                'Approved school request not found.'
            )
        return value


class StaffOnboardingSerializer(serializers.Serializer):
    """Serializer for onboarding staff members."""
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    staff_number = serializers.CharField(max_length=50)
    gender = serializers.ChoiceField(choices=['M', 'F'])
    date_of_birth = serializers.DateField()
    department = serializers.CharField(max_length=100)
    position = serializers.CharField(max_length=100)
    role_codes = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )


class ParentOnboardingSerializer(serializers.Serializer):
    """Serializer for onboarding parents."""
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)
    relationship = serializers.ChoiceField(
        choices=['father', 'mother', 'guardian', 'other']
    )
    password = serializers.CharField(min_length=8, required=False, allow_blank=True)


class SchoolSetupStatusSerializer(serializers.Serializer):
    """Serializer for school setup status."""
    has_academic_year = serializers.BooleanField()
    has_sections = serializers.BooleanField()
    has_classes = serializers.BooleanField()
    has_subjects = serializers.BooleanField()
    has_grade_scales = serializers.BooleanField()
