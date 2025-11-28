from django.db import models
from django.conf import settings


class Grievance(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_APPROVED = 'Approved'
    STATUS_REJECTED = 'Rejected'
    STATUS_UNDER_REVIEW = 'Under Review'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
    ]

    CONTACT_EMAIL = 'email'
    CONTACT_PHONE = 'phone'

    CONTACT_CHOICES = [
        (CONTACT_EMAIL, 'Email'),
        (CONTACT_PHONE, 'Phone'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grievances')
    grievance_id = models.CharField(max_length=32, unique=True, blank=True)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    preferred_contact = models.CharField(max_length=10, choices=CONTACT_CHOICES, default=CONTACT_EMAIL,blank=True,null=True)
    attachment_url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    officer_remark = models.TextField(blank=True, null=True)
    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_grievances",
        limit_choices_to={"role": "officer"}
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.grievance_id} - {self.subject}"
