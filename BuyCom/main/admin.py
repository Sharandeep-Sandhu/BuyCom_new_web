from django.contrib import admin
from .models import Category, Product, PriceHistory, ContactInquiry


# ─── CATEGORY ADMIN ─────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)


# ─── PRODUCT ADMIN ─────────────────────────────────────

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'price_per_ton',
        'is_active', 'is_featured', 'updated_at'
    )
    list_filter = ('category', 'is_active', 'is_featured')
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)
    readonly_fields = ('created_at', 'updated_at')


# ─── PRICE HISTORY ADMIN ───────────────────────────────

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'old_price', 'new_price', 'changed_at')
    list_filter = ('changed_at',)
    search_fields = ('product__name',)


# ─── CONTACT INQUIRY ADMIN ─────────────────────────────

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'company')
    readonly_fields = ('created_at',)