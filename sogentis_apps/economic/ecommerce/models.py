#economic/ecommerce/models.py
from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    price = models.PositiveIntegerField(verbose_name="Prix (XOF)")
    description = models.TextField()
    fiche_technique = models.TextField(blank=True, help_text="Fiche technique, caractéristiques (HTML ou Markdown accepté)")
    image = models.ImageField(upload_to="economic/products/")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")
    is_new = models.BooleanField(default=False, verbose_name="Nouveau produit")
    is_active = models.BooleanField(default=True, verbose_name="Produit actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payée'),
        ('shipped', 'Expédiée'),
        ('done', 'Livrée'),
        ('cancel', 'Annulée'),
    ]
    tracking_code = models.CharField(max_length=12, unique=True, blank=True)
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = get_random_string(10).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.tracking_code}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()  # copie prix à la commande

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"