from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    # 🏡 Personal Info
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    taluka = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = models.FileField(upload_to="documents/profile_photos/", blank=True, null=True)

    # 🏞️ Land Info
    land_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    ownership_type = models.CharField(max_length=20, blank=True, null=True)
    land_proof = models.FileField(upload_to="documents/land_proofs/", blank=True, null=True)

    # 🏦 Bank & ID Info
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    ifsc_code = models.CharField(max_length=15, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    pan_card = models.FileField(upload_to="documents/pan_cards/", blank=True, null=True)
    aadhaar_card = models.FileField(upload_to="documents/aadhaar_cards/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name}'s Profile"
