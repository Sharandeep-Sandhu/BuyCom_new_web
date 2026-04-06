from email.mime import base

from rest_framework.permissions import AllowAny
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category, Product, PriceHistory, ContactInquiry
from django.shortcuts import render
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers   import MultiPartParser, FormParser, JSONParser



from .serializers import (
    CategoryListSerializer, CategoryDetailSerializer,
    ProductSerializer, PriceHistorySerializer, ContactInquirySerializer,
)



def home(request):
    """Customer website homepage"""
    return render(request, 'index.html')

def admin_dashboard(request):
    """Custom admin panel dashboard"""
    return render(request, 'index_admin.html')


# ─────────────────────────────────────────────────────────────────────
# PUBLIC ENDPOINTS  (Customer Site 1)
# ─────────────────────────────────────────────────────────────────────

class PublicCategoryListView(generics.ListAPIView):
    """GET /api/categories/  — list active categories with product count."""
    serializer_class = CategoryListSerializer

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class PublicCategoryDetailView(generics.RetrieveAPIView):
    """GET /api/categories/<slug>/  — category + its active products."""
    serializer_class = CategoryDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class PublicProductListView(generics.ListAPIView):
    """GET /api/products/?category=<slug>  — active products, optional filter."""
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related('category')
        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs


class PublicProductDetailView(generics.RetrieveAPIView):
    """GET /api/products/<slug>/"""
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    queryset = Product.objects.filter(is_active=True)

@csrf_exempt
@api_view(['POST'])
def submit_contact(request):
    """POST /api/contact/  — submit an inquiry from the customer site."""
    serializer = ContactInquirySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'success': True, 'message': 'Inquiry submitted successfully.'},
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {'success': False, 'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


# ─────────────────────────────────────────────────────────────────────
# ADMIN ENDPOINTS  (Control Panel Site 2)
# ─────────────────────────────────────────────────────────────────────
@csrf_exempt
@api_view(['GET'])
def dashboard_stats(request):
    """GET /api/admin/stats/  — summary numbers for the dashboard."""
    return Response({
        'total_categories':  Category.objects.count(),
        'active_categories': Category.objects.filter(is_active=True).count(),
        'active_products':   Product.objects.filter(is_active=True).count(),
        'inactive_products': Product.objects.filter(is_active=False).count(),
        'total_products':    Product.objects.count(),
        'total_inquiries':   ContactInquiry.objects.count(),
        'unread_inquiries':  ContactInquiry.objects.filter(is_read=False).count(),
    })


# ── Categories ────────────────────────────────────────────────────────

class AdminCategoryListCreateView(generics.ListCreateAPIView):
    """GET /api/admin/categories/   POST /api/admin/categories/"""
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()

    def perform_create(self, serializer):
        name = serializer.validated_data.get('name', '')
        slug = serializer.validated_data.get('slug') or slugify(name)
        serializer.save(slug=slug)


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / PATCH / DELETE /api/admin/categories/<id>/"""
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()


# ── Products ──────────────────────────────────────────────────────────
@permission_classes([AllowAny])
class AdminProductListCreateView(generics.ListCreateAPIView):
    """
    GET  /admin/products/?category=<slug>
    POST /admin/products/                  (multipart or JSON)
    """
    serializer_class   = ProductSerializer
    permission_classes = [AllowAny]
    # Accept both JSON and multipart/form-data (for image uploads)
    parser_classes     = [MultiPartParser, FormParser, JSONParser]
 
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx
 
    def get_queryset(self):
        qs  = Product.objects.all().select_related('category')
        cat = self.request.query_params.get('category')
        if cat:
            qs = qs.filter(category__slug=cat)
        return qs
 
    def perform_create(self, serializer):
        name     = serializer.validated_data.get('name', '')
        category = serializer.validated_data.get('category')
        cat_slug = category.slug if category else 'product'
        slug     = slugify(f'{cat_slug}-{name}')[:250]
        # Ensure uniqueness
        base, counter = slug, 1
        while Product.objects.filter(slug=slug).exists():
            slug = f'{base}-{counter}'
            counter += 1
        serializer.save(slug=slug)


class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PUT / PATCH / DELETE /api/admin/products/<id>/"""
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def perform_update(self, serializer):
        product   = self.get_object()
        new_price = serializer.validated_data.get('price_per_ton')
        if new_price is not None and new_price != product.price_per_ton:
            PriceHistory.objects.create(
                product   = product,
                old_price = product.price_per_ton,
                new_price = new_price,
                note      = 'Updated via admin panel',
            )
        serializer.save()
    def get(self, request, id):
        product = Product.objects.get(id=id)
        return Response({
            "id": product.id,
            "price": product.price
        })

@csrf_exempt
@api_view(['PATCH'])
def update_product_price(request, pk):
    """PATCH /api/admin/products/<id>/price/  — quick price update."""
    product   = get_object_or_404(Product, pk=pk)
    new_price = request.data.get('price_per_ton')
    note      = request.data.get('note', 'Price updated via admin')

    if new_price is None:
        return Response({'error': 'price_per_ton is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        new_price = float(new_price)
    except (TypeError, ValueError):
        return Response({'error': 'Invalid price value.'}, status=status.HTTP_400_BAD_REQUEST)

    PriceHistory.objects.create(
        product   = product,
        old_price = product.price_per_ton,
        new_price = new_price,
        note      = note,
    )
    product.price_per_ton = new_price
    product.save()
    return Response({'success': True, 'product': ProductSerializer(product).data})

@csrf_exempt
@api_view(['PATCH'])
def toggle_product_status(request, pk):
    """PATCH /api/admin/products/<id>/toggle/  — flip is_active."""
    product          = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save()
    return Response({'success': True, 'is_active': product.is_active})

@csrf_exempt
@api_view(['PATCH'])
def toggle_price_visible(request, pk):
    """PATCH /api/admin/products/<id>/price-visible/  — show/hide price."""
    product               = get_object_or_404(Product, pk=pk)
    product.price_visible = not product.price_visible
    product.save()
    return Response({'success': True, 'price_visible': product.price_visible})


# ── Price History ─────────────────────────────────────────────────────

class PriceHistoryListView(generics.ListAPIView):
    """GET /api/admin/products/<product_id>/history/"""
    serializer_class = PriceHistorySerializer

    def get_queryset(self):
        return PriceHistory.objects.filter(product_id=self.kwargs['product_id'])


# ── Inquiries ─────────────────────────────────────────────────────────

class AdminInquiryListView(generics.ListAPIView):
    """GET /api/admin/inquiries/"""
    serializer_class = ContactInquirySerializer

    def get_queryset(self):
        qs     = ContactInquiry.objects.all()
        status = self.request.query_params.get('status')
        if status == 'unread':
            qs = qs.filter(is_read=False)
        elif status == 'read':
            qs = qs.filter(is_read=True)
        return qs

@csrf_exempt
@api_view(['PATCH'])
def mark_inquiry_read(request, pk):
    """PATCH /api/admin/inquiries/<id>/read/"""
    inquiry         = get_object_or_404(ContactInquiry, pk=pk)
    inquiry.is_read = True
    inquiry.save()
    return Response({'success': True})

@csrf_exempt
@api_view(['DELETE'])
def delete_inquiry(request, pk):
    """DELETE /api/admin/inquiries/<id>/"""
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    inquiry.delete()
    return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)