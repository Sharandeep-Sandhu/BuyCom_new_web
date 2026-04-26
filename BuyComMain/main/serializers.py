from rest_framework import serializers
from .models import Category, ProductType, ProductVariant, PriceHistory, ContactInquiry
from django.db import models


class ProductVariantSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="product_type.category.name", read_only=True
    )
    category_slug = serializers.CharField(
        source="product_type.category.slug", read_only=True
    )
    product_type_name = serializers.CharField(
        source="product_type.name", read_only=True
    )
    base_price_rate = serializers.ReadOnlyField(source="base_price.base_rate")
    base_price_name = serializers.ReadOnlyField(source="base_price.name")
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class ProductTypeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    variant_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductType
        fields = "__all__"
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url

    def get_variant_count(self, obj):
        """Count of active variants under this product type"""
        return obj.variants.filter(is_active=True).count()


class CategoryListSerializer(serializers.ModelSerializer):
    product_type_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon", "is_active", "product_type_count"]
        extra_kwargs = {
            "slug": {"required": False, "allow_blank": True},
        }

    def get_product_type_count(self, obj):
        """Count of active ProductTypes under this category"""
        return obj.product_types.filter(is_active=True).count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    product_types = serializers.SerializerMethodField()
    product_type_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "is_active",
            "product_types",
            "product_type_count",
        ]

    def get_product_types(self, obj):
        """Return active ProductTypes with their variant count"""
        types = obj.product_types.filter(is_active=True)
        return ProductTypeSerializer(types, many=True, context=self.context).data

    def get_product_type_count(self, obj):
        """Count of active ProductTypes under this category"""
        return obj.product_types.filter(is_active=True).count()


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ["id", "variant", "old_rate", "new_rate", "changed_at", "note"]
        read_only_fields = ["id", "changed_at"]


class ContactInquirySerializer(serializers.ModelSerializer):
    product_interest = serializers.CharField(
        allow_blank=True, allow_null=True, required=False, write_only=True
    )

    product_interest_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ContactInquiry
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "company",
            "product_interest",
            "product_interest_display",
            "message",
            "created_at",
            "is_read",
        ]
        read_only_fields = ["id", "created_at", "is_read", "product_interest_display"]

    def get_product_interest_display(self, obj):
        return obj.product_interest.name if obj.product_interest else None

    def create(self, validated_data):
        product_name = validated_data.pop("product_interest", None)

        if product_name:
            product_name = str(product_name).strip()

            # Try to find existing ProductType
            product_type = ProductType.objects.filter(name__iexact=product_name).first()

            if not product_type:
                # Try to find by slug (in case frontend sends slug)
                product_type = ProductType.objects.filter(
                    slug__iexact=product_name
                ).first()

            if not product_type:
                # Last resort: treat it as Category and create under it
                category = Category.objects.filter(
                    models.Q(name__iexact=product_name)
                    | models.Q(slug__iexact=product_name)
                ).first()

                if category:
                    # Create ProductType under this category
                    product_type = ProductType.objects.create(
                        category=category,
                        name=product_name,
                        description="Auto-created from customer inquiry",
                        is_active=True,
                    )
                else:
                    # Fallback: create with first active category
                    category = Category.objects.filter(is_active=True).first()
                    if not category:
                        # Create a default category if none exists
                        category = Category.objects.create(
                            name="General", is_active=True
                        )

                    product_type = ProductType.objects.create(
                        category=category,
                        name=product_name,
                        description="Auto-created from customer inquiry",
                        is_active=True,
                    )

            validated_data["product_interest"] = product_type

        return super().create(validated_data)
