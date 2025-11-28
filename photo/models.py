from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('bank_passbook', 'Bank Passbook / Cancelled Cheque'),
        ('scope_certificate', 'Scope Certificate of Organic Farming'),
        ('annexure_copy', 'Copy of Annexure in Group Certification'),
        ('residue_fee_receipt', 'Receipt of fee paid for residue testing'),
        ('divyang_certificate', 'Copy of Divyang Certificate (if applicable)'),
        ('joint_account_letter', "Joint Account Holder's Construction Letter"),
        ('residue_testing_copy', 'Copy of residue testing'),
        ('aadhar_card', 'Aadhar Card'),
        ('land_document', 'Copy of 7/12 and 8-A'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='photo_documents',        # <= unique name
        related_query_name='photo_document'    # <= optional: useful in queries
    )
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=50)
    file = CloudinaryField('document', resource_type='auto')
    resource_type = models.CharField(max_length=10, blank=True, null=True)     # Optional now
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        user_identifier = self.user.email if hasattr(self.user, 'email') else str(self.user.id)
        return f"{user_identifier} - {self.title}"
