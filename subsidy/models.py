from django.db import models
from cloudinary.models import CloudinaryField

from django.contrib.auth.models import User
from django.conf import settings


class Document(models.Model):
   
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subsidy_documents',     # <= unique name
        related_query_name='subsidy_document' # <= optional
    )
    document_type = models.CharField(max_length=100)
    document_number = models.CharField(max_length=100, blank=True, null=True)
    file = CloudinaryField('file', folder='documents/subsidy_documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('owner', 'document_type')
    
    
    def __str__(self):
        return f"{self.owner.full_name} - {self.document_type}"


class Subsidy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    documents_required = models.JSONField(default=list)

    def __str__(self):
        return self.title


class SubsidyApplication(models.Model):
   
    
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subsidy_applications')
    subsidy = models.ForeignKey(
    'app.Subsidy',
    on_delete=models.SET_NULL,
    related_name='applications',
    null=True,
    blank=True
)
    full_name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=20)
    email = models.CharField(max_length=255)
    aadhaar = models.CharField(max_length=20)
    address = models.TextField()
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    taluka = models.CharField(max_length=100)
    village = models.CharField(max_length=100)

    land_area = models.FloatField()
    land_unit = models.CharField(max_length=50)
    soil_type = models.CharField(max_length=50)
    ownership = models.CharField(max_length=50)

    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    ifsc = models.CharField(max_length=20)

    documents = models.ManyToManyField(Document, related_name="applications")

    submitted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'subsidy')
    def __str__(self):
        return f"{self.user.full_name} - {self.subsidy.title}"
