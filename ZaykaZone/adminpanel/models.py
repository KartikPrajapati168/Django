from django.db import models
from django.utils.text import slugify

# Create your models here.
class CuisinePageContent(models.Model):
    cuisine_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.cuisine_name)
        super().save(*args, **kwargs)
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    background_image = models.ImageField(
        upload_to='cuisine_banners/', blank=True, null=True
    )

    class Meta:
        verbose_name = "Cuisine Page Content"
        verbose_name_plural = "Cuisine Page Contents"

    def __str__(self):
        return f"{self.cuisine_name} Page Content"
    