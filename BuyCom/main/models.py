from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name        = models.CharField(max_length=100)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=10, blank=True, help_text='Emoji icon')
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category        = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name            = models.CharField(max_length=200)
    slug            = models.SlugField(unique=True, max_length=250)
    description     = models.TextField(blank=True)
    
    # ── IMAGE ──────────────────────────────────────────────────────────
    image           = models.ImageField(
                        upload_to='products/',
                        blank=True,
                        null=True,
                        help_text='Product image (JPEG/PNG, max 5 MB recommended)'
                      )
    # Specifications
    thickness_range = models.CharField(max_length=120, blank=True)
    width_range     = models.CharField(max_length=120, blank=True)
    length_range    = models.CharField(max_length=120, blank=True)
    size_info       = models.TextField(blank=True, help_text='Size options e.g. channel sizes')
    grade           = models.CharField(max_length=400, blank=True)

    # Pricing
    price_per_ton   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          help_text='Price in INR per metric ton')
    price_unit      = models.CharField(max_length=30, default='per MT')
    price_visible   = models.BooleanField(default=True, help_text='Show price on customer site')

    # Flags
    is_active       = models.BooleanField(default=True)
    is_featured     = models.BooleanField(default=False)
    order           = models.PositiveIntegerField(default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.category.name} — {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f'{self.category.slug}-{self.name}')
            self.slug = base[:250]
        super().save(*args, **kwargs)


class PriceHistory(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_price  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_price  = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)
    note       = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f'{self.product.name}: ₹{self.new_price} on {self.changed_at:%d %b %Y}'


class ContactInquiry(models.Model):
    name             = models.CharField(max_length=100)
    email            = models.EmailField()
    phone            = models.CharField(max_length=20, blank=True)
    company          = models.CharField(max_length=150, blank=True)
    product_interest = models.CharField(max_length=200, blank=True)
    message          = models.TextField()
    created_at       = models.DateTimeField(auto_now_add=True)
    is_read          = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Contact Inquiries'

    def __str__(self):
        return f'{self.name} — {self.created_at:%d %b %Y}'