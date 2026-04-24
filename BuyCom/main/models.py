from django.db import models
from django.utils.text import slugify
from decimal import Decimal


class Category(models.Model):
    """Main Categories: Mild Steel (MS), Stainless Steel (SS), Structural Steel, etc."""
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


class BasePrice(models.Model):
    """Daily Base Rates (Ingot, Flat Base, Angle Base, Pipe Base, etc.)"""
    name        = models.CharField(max_length=150, help_text="e.g. Ingot, MS Flat Base, Angle Base")
    base_rate   = models.DecimalField(max_digits=12, decimal_places=2)
    date        = models.DateField()
    note        = models.TextField(blank=True, help_text="Special notes like 'Jointless pipe +500'")
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'name']
        unique_together = ('name', 'date')

    def __str__(self):
        return f"{self.name} - ₹{self.base_rate} ({self.date})"


class ProductType(models.Model):
    """Main Product Types: Flat, Angle, Channel, Round Bar, HR Coil, SS Pipe, TMT, Beam, etc."""
    category        = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_types')
    
    name            = models.CharField(max_length=150)
    slug            = models.SlugField(unique=True, max_length=200)
    description     = models.TextField(blank=True)

    # Image for the Product Type (Main category image - e.g., image of Flat bars)
    image           = models.ImageField(
                        upload_to='products/types/',
                        blank=True,
                        null=True,
                        help_text='Main image for this product type (e.g., HR Coil, Angle, etc.)'
                      )

    # General ranges (from your website images)
    thickness_range = models.CharField(max_length=120, blank=True, help_text="e.g. 5 - 65 mm")
    width_range     = models.CharField(max_length=120, blank=True, help_text="e.g. 25 - 500 mm")
    length_range    = models.CharField(max_length=120, blank=True)
    size_info       = models.TextField(blank=True, help_text="Common sizes like 75x40, 100x50, 16mm etc.")

    grade           = models.CharField(max_length=400, blank=True, help_text="e.g. IS2062, 304, E250")
    icon            = models.CharField(max_length=10, blank=True)

    is_active       = models.BooleanField(default=True)
    order           = models.PositiveIntegerField(default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', 'name']
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} → {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.slug}-{self.name}")
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """Individual sizes with pricing - Matches your Excel files perfectly"""
    product_type   = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='variants')

    # Size as shown in Excel
    size_label     = models.CharField(max_length=100, 
                                      help_text="Exact size from Excel: 25x5, 75*40LC, 19od x 03 Kg, 50mm")

    description    = models.CharField(max_length=200, blank=True)

    # Optional specific image for this variant (useful for popular sizes)
    image          = models.ImageField(
                        upload_to='products/variants/',
                        blank=True,
                        null=True,
                        help_text='Optional image for this specific size/variant'
                      )

    # Pricing (Core from your Excel)
    base_price     = models.ForeignKey(BasePrice, on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='variants')
    differential   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                         help_text="Differential from base rate")
    final_rate     = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                         help_text="Final rate per ton")

    weight_kg      = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                         help_text="Weight per piece in Kg (especially for pipes)")

    # Special flags
    is_base_rate   = models.BooleanField(default=False, help_text="Marked as 'B' in Excel")
    has_range      = models.BooleanField(default=False, help_text="Rate is a range like 9000TO9500")

    extra_note     = models.CharField(max_length=200, blank=True,
                                      help_text="e.g. 500 Extra, Ask During Transaction, 9000-9500")

    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['size_label']
        unique_together = ('product_type', 'size_label')

    def __str__(self):
        rate = f"₹{self.final_rate}" if self.final_rate else "N/A"
        return f"{self.product_type.name} - {self.size_label} → {rate}"

    def save(self, *args, **kwargs):
        # Auto calculate final_rate if base_price and differential are available
        if self.final_rate is None and self.differential is not None and self.base_price:
            self.final_rate = self.base_price.base_rate + self.differential
        super().save(*args, **kwargs)


class PriceHistory(models.Model):
    """Track price changes"""
    variant     = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='price_history')
    old_rate    = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_rate    = models.DecimalField(max_digits=12, decimal_places=2)
    changed_at  = models.DateTimeField(auto_now_add=True)
    note        = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.variant} → ₹{self.new_rate}"


class ContactInquiry(models.Model):
    name             = models.CharField(max_length=100)
    email            = models.EmailField()
    phone            = models.CharField(max_length=20, blank=True)
    company          = models.CharField(max_length=150, blank=True)
    product_interest = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, blank=True)
    message          = models.TextField()
    created_at       = models.DateTimeField(auto_now_add=True)
    is_read          = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Contact Inquiries'

    def __str__(self):
        return f'{self.name} — {self.created_at:%d %b %Y}'