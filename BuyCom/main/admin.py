from django.contrib import admin
from .models import (
    Category, BasePrice, ProductType, 
    ProductVariant, PriceHistory, ContactInquiry
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BasePrice)
class BasePriceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_rate', 'date', 'is_active']
    list_filter = ['is_active', 'date']
    search_fields = ['name']


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'grade', 'is_active', 'order']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description', 'grade']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['size_label', 'product_type', 'final_rate', 'differential', 
                    'weight_kg', 'is_active']
    list_filter = ['product_type', 'is_active', 'is_base_rate']
    search_fields = ['size_label', 'description', 'extra_note']
    raw_id_fields = ['product_type', 'base_price']


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['variant', 'old_rate', 'new_rate', 'changed_at', 'note']
    list_filter = ['changed_at']
    search_fields = ['variant__size_label', 'variant__product_type__name', 'note']
    date_hierarchy = 'changed_at'


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'company', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at']