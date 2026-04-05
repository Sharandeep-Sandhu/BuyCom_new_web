from django.urls import path
from . import views

urlpatterns = [
    # Frontend routes
    path('', views.home, name='home'),                    # ← root = index.html
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),    


    # ── PUBLIC (Customer Site 1) ──────────────────────────────────────────
    path('categories/',                  views.PublicCategoryListView.as_view(),   name='pub-category-list'),
    path('categories/<slug:slug>/',      views.PublicCategoryDetailView.as_view(), name='pub-category-detail'),
    path('products/',                    views.PublicProductListView.as_view(),    name='pub-product-list'),
    path('products/<slug:slug>/',        views.PublicProductDetailView.as_view(),  name='pub-product-detail'),
    path('contact/',                     views.submit_contact,                     name='submit-contact'),
 
    # ── ADMIN (Control Panel Site 2) ─────────────────────────────────────
    path('admin/stats/',                 views.dashboard_stats,                    name='admin-stats'),
 
    # Categories
    path('admin/categories/',            views.AdminCategoryListCreateView.as_view(), name='admin-cat-list'),
    path('admin/categories/<int:pk>/',   views.AdminCategoryDetailView.as_view(),    name='admin-cat-detail'),
 
    # Products
    path('admin/products/',              views.AdminProductListCreateView.as_view(), name='admin-prod-list'),
    path('admin/products/<int:pk>/',     views.AdminProductDetailView.as_view(),     name='admin-prod-detail'),
    path('admin/products/<int:pk>/price/',         views.update_product_price,  name='admin-prod-price'),
    path('admin/products/<int:pk>/toggle/',        views.toggle_product_status, name='admin-prod-toggle'),
    path('admin/products/<int:pk>/price-visible/', views.toggle_price_visible,  name='admin-prod-price-visible'),
    path('admin/products/<int:product_id>/history/', views.PriceHistoryListView.as_view(), name='admin-price-history'),
 
    # Inquiries
    path('admin/inquiries/',             views.AdminInquiryListView.as_view(), name='admin-inq-list'),
    path('admin/inquiries/<int:pk>/read/',   views.mark_inquiry_read, name='admin-inq-read'),
    path('admin/inquiries/<int:pk>/delete/', views.delete_inquiry,    name='admin-inq-delete'),
]