from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


class CustomUserManager(BaseUserManager):
    # Moved mobile_number to have a default value of None so it is truly optional
    def create_user(self, full_name, email_address, mobile_number=None, password=None, aadhaar_number=None, role="farmer"):
        if not email_address:
            raise ValueError("User must provide an email address")

        user = self.model(
            full_name=full_name,
            mobile_number=mobile_number,
            email_address=self.normalize_email(email_address),
            aadhaar_number=aadhaar_number,
            role=role,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, full_name, email_address, password, mobile_number=None, aadhaar_number=None):
        if not password:
            raise ValueError("Superuser must have a password.")
        if not email_address:
            raise ValueError("Superuser must have an email address.")
            
        user = self.create_user(
            full_name=full_name,
            email_address=email_address,
            mobile_number=mobile_number,
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
    # Removed "mobile_number" from REQUIRED_FIELDS
    REQUIRED_FIELDS = ["full_name"]    

    def __str__(self):
        return self.full_name


class PasswordResetOTP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email_address} - {self.otp}'
    

class EmailVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class OTP(models.Model):
    # Removed the obsolete mobile and login choices
    PURPOSES = [
        ("email_verify", "Email Verification"),
        ("forgot_password", "Forgot Password"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSES)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email_address} - {self.purpose} - {self.otp}"