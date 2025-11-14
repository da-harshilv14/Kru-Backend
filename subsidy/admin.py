from django.contrib import admin
from .models import Document, Subsidy, SubsidyApplication

admin.site.register(Document)
admin.site.register(Subsidy)
admin.site.register(SubsidyApplication)