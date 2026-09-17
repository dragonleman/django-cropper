from django.contrib import admin

from .models import CroppedImage


@admin.register(CroppedImage)
class CroppedImageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "created_at",
        "original",
        "cropped",
    )

    readonly_fields = (
        "created_at",
    )
