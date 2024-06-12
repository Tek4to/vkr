from django.contrib import admin

# Register your models here.
from medemail import models

@admin.register(models.MedEmail)
class MedEmailAdmin(admin.ModelAdmin):
  pass