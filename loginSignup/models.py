from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Q, UniqueConstraint
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, full_name, mobile_number, email_address, password=None, aadhaar_number=None, role="farmer"):
        if not mobile_number or not email_address:
            raise ValueError("User must provide either a mobile number and an email address")

        user = self.model(
            full_name=full_name,
            mobile_number=mobile_number,
            email_address=email_address,
            aadhaar_number=aadhaar_number,
            role=role,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, full_name, mobile_number, email_address, password, aadhaar_number=None):
        user = self.create_user(
            full_name=full_name,
            mobile_number=mobile_number,
            email_address=email_address,
            password=password,
            aadhaar_number=aadhaar_number,
            role="admin"
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("farmer", "Farmer"),
        ("admin", "Admin"),
        ("officer", "Officer"),
        ("subsidy_provider", "Subsidy Provider"),
    ]

    full_name = models.CharField(max_length=100)
    mobile_number = PhoneNumberField(unique=True, blank=True, null=True)
    email_address = models.EmailField(unique=True, max_length=254, blank=True, null=True)
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="farmer")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email_address"   # login using email by default
    REQUIRED_FIELDS = ["full_name", "mobile_number"]    # extra fields required when creating superuser

    def __str__(self):
        return self.full_name
from django.db import models
from django.conf import settings

class PasswordResetOTP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.otp}'