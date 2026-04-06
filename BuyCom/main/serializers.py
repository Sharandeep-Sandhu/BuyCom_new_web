from rest_framework import serializers
from .models import Category, Product, PriceHistory, ContactInquiry



class ProductSerializer(serializers.ModelSerializer):
    """
    Full product serializer.
    • `category`   — writable FK (accepts integer ID on write)
    • `category_name` — read-only helper
    • `image`      — writable ImageField (multipart upload)
    • `image_url`  — read-only absolute URL built from request context
    """
    category_name = serializers.SerializerMethodField(read_only=True)
    image_url     = serializers.SerializerMethodField(read_only=True)
 
    # Allow image to be optional on both create and update
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        use_url=True,
    )
 
    class Meta:
        model  = Product
        # fields = [
        #     'id', 'category', 'category_name',
        #     'name', 'slug', 'description',
        #     'image', 'image_url',
        #     'thickness_range', 'width_range', 'length_range', 'size_info', 'grade',
        #     'price_per_ton', 'price_unit', 'price_visible',
        #     'is_active', 'is_featured', 'order',
        #     'created_at', 'updated_at',
        # ]
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']
 
    def get_category_name(self, obj):
        return obj.category.name if obj.category_id else ''
 
    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


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