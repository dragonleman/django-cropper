from django.db import models


class CroppedImage(models.Model):

    original = models.ImageField(upload_to="originals/")

    cropped = models.ImageField(upload_to="cropped/")

    crop_x = models.FloatField(default=0)
    crop_y = models.FloatField(default=0)
    crop_width = models.FloatField(default=0)
    crop_height = models.FloatField(default=0)

    image_transform = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image {self.id}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Image croppée"
        verbose_name_plural = "Images croppées"
