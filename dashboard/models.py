from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cloud_profile")

    # 🏡 Personal Info
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = CloudinaryField('file', folder='documents/profile_photos/', blank=True, null=True)

    # 🏞️ Land Info
    land_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    ownership_type = models.CharField(max_length=20, blank=True, null=True)
    land_proof = CloudinaryField('file', folder='documents/land_proofs/', blank=True, null=True)

    # 🏦 Bank & ID Info
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=15, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    pan_card = CloudinaryField('file', folder='documents/pan_cards/', blank=True, null=True)
    aadhaar_card = CloudinaryField('file', folder='documents/aadhaar_cards/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name}'s Profile"
