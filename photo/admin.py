from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'document_type_label', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title', 'document_number', 'user__email')

    @admin.display(description='Document type')
    def document_type_label(self, obj):
        return obj.get_document_type_display()
