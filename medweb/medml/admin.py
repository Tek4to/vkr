from django.contrib import admin
from django_use_email_as_username.admin import BaseUserAdmin
from medml import models

from django.utils.translation import gettext_lazy as _


class MedWorkerAdmin(BaseUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "fathers_name")}),
        ("Медицинская организация", {"fields": ("med_organization","job")}),
        ("Экспертная информация", {"fields": ("is_remote_worker","expert_details")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    list_display = ("email", "first_name", "last_name", "fathers_name", "is_staff")
    search_fields = ("email", "first_name", "last_name", "fathers_name")
    ordering = ("email",)



admin.site.register(models.MedWorker, MedWorkerAdmin)


@admin.register(models.Patient)
class PatientAdmin(admin.ModelAdmin):
    pass

@admin.register(models.UZIImageGroup)
class UZIImageGroupAdmin(admin.ModelAdmin):
    pass

@admin.register(models.PatientCard)
class PatientCardAdmin(admin.ModelAdmin):
    pass

@admin.register(models.UZIDevice)
class UZIDeviceAdmin(admin.ModelAdmin):
    pass

@admin.register(models.OriginalImage)
class OriginalImageAdmin(admin.ModelAdmin):
    pass

@admin.register(models.SegmentationImage)
class SegmentationImageAdmin(admin.ModelAdmin):
    pass

@admin.register(models.BoxImage)
class BoxImageAdmin(admin.ModelAdmin):
    pass

@admin.register(models.MLModel)
class MLModelAdmin(admin.ModelAdmin):
    pass
