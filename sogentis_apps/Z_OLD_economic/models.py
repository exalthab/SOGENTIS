# from django.db import models
# from django.utils.text import slugify
# from django.utils.timezone import now


# class Category(models.Model):
#     name = models.CharField(max_length=50)
#     slug = models.SlugField(unique=True)

#     class Meta:
#         verbose_name = "Catégorie"
#         verbose_name_plural = "Catégories"
#         ordering = ['name']

#     def __str__(self):
#         return self.name


# class Product(models.Model):
#     category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField(max_length=120)
#     slug = models.SlugField(unique=True, blank=True)
#     price = models.PositiveIntegerField()
#     description = models.TextField()
#     image = models.ImageField(upload_to="economic/products/")
#     is_new = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return self.name

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             base_slug = slugify(self.name)
#             slug = base_slug
#             num = 1
#             while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#                 slug = f"{base_slug}-{num}"
#                 num += 1
#             self.slug = slug
#         super().save(*args, **kwargs)
