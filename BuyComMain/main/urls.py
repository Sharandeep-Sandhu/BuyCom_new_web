from django.urls import path
from . import views

urlpatterns = [
    # ====================== FRONTEND PAGES ======================
    path("", views.home, name="home"),  # Customer Homepage
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    # ====================== PUBLIC API (Customer Site) ======================
    path(
        "api/categories/",
        views.PublicCategoryListView.as_view(),
        name="pub-category-list",
    ),
    path(
        "api/categories/<slug:slug>/",
        views.PublicCategoryDetailView.as_view(),
        name="pub-category-detail",
    ),
    path(
        "api/product-types/",
        views.PublicProductTypeListView.as_view(),
        name="pub-product-type-list",
    ),
    path(
        "api/product-variants/",
        views.PublicProductVariantListView.as_view(),
        name="pub-product-variant-list",
    ),
    path(
        "api/product-variants/<int:pk>/",
        views.PublicProductVariantDetailView.as_view(),
        name="pub-product-variant-detail",
    ),
    # path("api/contact/", views.submit_contact, name="submit-contact"),
    # ====================== ADMIN API ======================
    path("api/admin/stats/", views.dashboard_stats, name="admin-stats"),
    # ── Categories ─────────────────────────────────────
    path(
        "api/admin/categories/",
        views.AdminCategoryListCreateView.as_view(),
        name="admin-category-list",
    ),
    path(
        "api/admin/categories/<int:pk>/",
        views.AdminCategoryDetailView.as_view(),
        name="admin-category-detail",
    ),
    # ── Product Types ──────────────────────────────────
    path(
        "api/admin/product-types/",
        views.AdminProductTypeListCreateView.as_view(),
        name="admin-product-type-list",
    ),
    path(
        "api/admin/product-types/<int:pk>/",
        views.AdminProductTypeDetailView.as_view(),
        name="admin-product-type-detail",
    ),
    # ── Product Variants (Main Pricing Items) ───────────
    path(
        "api/admin/product-variants/",
        views.AdminProductVariantListCreateView.as_view(),
        name="admin-product-variant-list",
    ),
    path(
        "api/admin/product-variants/<int:pk>/",
        views.AdminProductVariantDetailView.as_view(),
        name="admin-product-variant-detail",
    ),
    # ── Price History ──────────────────────────────────
    path(
        "api/admin/product-variants/<int:variant_id>/history/",
        views.PriceHistoryListView.as_view(),
        name="admin-price-history",
    ),
    # ── Excel Upload (Most Important Feature) ──────────
    path(
        "api/admin/upload-excel/", views.upload_excel_rates, name="upload-excel-rates"
    ),
    # ── Inquiries ──────────────────────────────────────
    path(
        "api/admin/inquiries/",
        views.AdminInquiryListView.as_view(),
        name="admin-inquiry-list",
    ),
    path("api/admin/inquiries/create/", views.create_inquiry, name="inquiry-create"),
    path(
        "api/admin/inquiries/<int:pk>/read/",
        views.mark_inquiry_read,
        name="admin-inquiry-read",
    ),
    path(
        "api/admin/inquiries/<int:pk>/delete/",
        views.delete_inquiry,
        name="admin-inquiry-delete",
    ),
    # Public Customer-facing endpoints
    path(
        "products/",
        views.PublicProductVariantListView.as_view(),
        name="public-products-list",
    ),
    # Keep your existing API endpoints under /api/
    path(
        "api/product-variants/",
        views.PublicProductVariantListView.as_view(),
        name="pub-product-variant-list",
    ),
    # ←←← ADD THIS NEW LINE ←←←
    path(
        "api/product-interests/",
        views.public_product_interest_list,
        name="public-product-interests",
    ),
    path(
        "api/product-types/",
        views.PublicProductTypeListView.as_view(),
        name="pub-product-type-list",
    ),
    path(
        "api/product-variants/",
        views.PublicProductVariantListView.as_view(),
        name="pub-product-variant-list",
    ),
    path(
        "api/product-variants/<int:pk>/",
        views.PublicProductVariantDetailView.as_view(),
        name="pub-product-variant-detail",
    ),
]
