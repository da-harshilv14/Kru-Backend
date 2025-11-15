from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

class Document(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subsidy_documents'
    )
    document_type = models.CharField(max_length=100)
    document_number = models.CharField(max_length=100, blank=True, null=True)
    file = CloudinaryField('file', folder='documents/subsidy_documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('owner', 'document_type')

    def __str__(self):
        return f"{self.owner.full_name} - {self.document_type}"


class SubsidyApplication(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subsidy_applications'
    )
    subsidy = models.ForeignKey(
        'app.Subsidy',
        on_delete=models.CASCADE,
        related_name='applications'
    )
    document_status = models.CharField(
    max_length=50,
    null=True,
    blank=True,
    default='Pending'
)

    
    application_id = models.PositiveIntegerField(unique=True, editable=False)

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
    updated_at = models.DateTimeField(auto_now=True)
    documents = models.ManyToManyField(Document, related_name="applications")

    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_subsidy_applications"
    )

    officer_comment = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)


    submitted_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Under Review', 'Under Review'),
        ('Rejected', 'Rejected'),
    ]


    status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='Pending',
    null=True,
    blank=True
)
    class Meta:
        unique_together = ('user', 'subsidy')

    def save(self, *args, **kwargs):
        if not self.application_id:
            last = SubsidyApplication.objects.order_by('-application_id').first()
            self.application_id = (int(last.application_id) + 1) if last else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.full_name} - {self.subsidy.title}"
