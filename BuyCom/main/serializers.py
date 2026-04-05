from rest_framework import serializers
from .models import Category, Product, PriceHistory, ContactInquiry


class ProductSerializer(serializers.ModelSerializer):
    # category_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'price_per_ton', 'description', 'is_active', 
            'price_visible', 'created_at', 'updated_at'
        ]
        # Make slug optional for creation (we generate it automatically)
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True},
        }
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else ''


class CategoryListSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        # fields = ['id', 'name', 'slug', 'description', 'icon', 'order', 'is_active', 'product_count', 'created_at', 'updated_at']
        fields = ['id', 'name', 'slug', 'icon', 'is_active', 'product_count']
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True},
        }
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    products      = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'order', 'is_active', 'products', 'product_count']

    def get_products(self, obj):
        return ProductSerializer(obj.products.filter(is_active=True), many=True).data

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['id', 'product', 'old_price', 'new_price', 'changed_at', 'note']
        read_only_fields = ['id', 'changed_at']


class ContactInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = ['id', 'name', 'email', 'phone', 'company', 'product_interest', 'message', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at', 'is_read']