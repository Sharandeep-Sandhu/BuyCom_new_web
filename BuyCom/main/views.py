from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.views import APIView

import pandas as pd
from decimal import Decimal
from datetime import date

from .models import (
    Category,
    BasePrice,
    ProductType,
    ProductVariant,
    PriceHistory,
    ContactInquiry,
)

from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    ProductTypeSerializer,
    ProductVariantSerializer,
    PriceHistorySerializer,
    ContactInquirySerializer,
)


# ====================== PUBLIC PAGES ======================
def home(request):
    """Customer website homepage"""
    return render(request, "index.html")


def admin_dashboard(request):
    """Admin dashboard page"""
    return render(request, "index_admin.html")


# ====================== PUBLIC API ENDPOINTS ======================


class PublicCategoryListView(generics.ListAPIView):
    """GET /api/categories/ - List all active categories"""

    serializer_class = CategoryListSerializer
    queryset = Category.objects.filter(is_active=True)


class PublicCategoryDetailView(generics.RetrieveAPIView):
    """GET /api/categories/<slug>/ - Category detail with product types"""

    serializer_class = CategoryDetailSerializer
    lookup_field = "slug"
    queryset = Category.objects.filter(is_active=True)


class PublicProductTypeListView(generics.ListAPIView):
    """GET /api/product-types/?category=<slug> - List product types"""

    serializer_class = ProductTypeSerializer

    def get_queryset(self):
        qs = ProductType.objects.filter(is_active=True).select_related("category")
        category_slug = self.request.query_params.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs


class PublicProductVariantListView(generics.ListAPIView):
    """GET /api/product-variants/?type=<slug> - List variants of a product type"""

    serializer_class = ProductVariantSerializer

    def get_queryset(self):
        qs = ProductVariant.objects.filter(is_active=True).select_related(
            "product_type__category"
        )
        type_slug = self.request.query_params.get("type")
        if type_slug:
            qs = qs.filter(product_type__slug=type_slug)
        return qs


@api_view(["PATCH"])
class ProductVariantRateUpdate(APIView):
    def patch(self, request, pk):
        variant = get_object_or_404(ProductVariant, pk=pk)

        new_rate = request.data.get("final_rate")
        note = request.data.get("note", "")

        if new_rate is None:
            return Response(
                {"error": "final_rate is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            variant.final_rate = float(new_rate)
            variant.save()

            # Optional: You can create a price history entry here if you want
            # PriceHistory.objects.create(variant=variant, old_rate=old_rate, new_rate=variant.final_rate, note=note)

            return Response({"success": True, "message": "Rate updated successfully"})
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid rate value"}, status=status.HTTP_400_BAD_REQUEST
            )


class PublicProductVariantDetailView(generics.RetrieveAPIView):
    """GET /api/product-variants/<int:pk>/"""

    serializer_class = ProductVariantSerializer
    queryset = ProductVariant.objects.filter(is_active=True)


# ====================== EXCEL UPLOAD - MAIN FEATURE ======================
# For Below API "upload_excel_rates"
# It finds or creates a ProductVariant with that size.
# It updates:
# Final Rate
# Differential
# Extra Note
@csrf_exempt
@api_view(["POST"])
def upload_excel_rates(request):
    if "file" not in request.FILES:
        return Response(
            {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    excel_file = request.FILES["file"]
    today = date.today()
    updated_count = 0
    structural_skips = 0
    data_failures = 0
    structural_skip_details = []
    data_failure_details = []
    errors = []

    STRUCTURAL_KEYWORDS = [
        "ingot",
        "base rate",
        "jointless pipe",
        "note :",
        "diffrential to be ask",
        "sr. no",
        "sr. no.",
        "grand total",
        "summary",
    ]

    SIZE_KEYWORDS = [
        "x",
        "*",
        "od",
        "mm",
        '"',
        "kg",
        "×",
        "inch",
        "rd",
        "sq",
        "flat",
        "angle",
    ]

    try:
        xl = pd.ExcelFile(excel_file, engine="openpyxl")

        with transaction.atomic():
            for sheet_name in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
                df = df.fillna("").astype(str).map(lambda x: x.strip())

                # ✅ FIX: Carry-forward state — persists across rows within a sheet
                prev_size_label = None
                prev_differential = None
                prev_final_rate = None
                prev_extra_note = ""
                prev_product_type_hint = None  # sheet/text hint for product type

                for idx, row in df.iterrows():
                    try:
                        row_list = row.tolist()
                        non_empty = [c for c in row_list if c and c.strip()]
                        full_text = " ".join(row_list).lower().strip()

                        if not full_text:
                            continue

                        # --- Structural skip: known header keywords ---
                        if any(kw in full_text for kw in STRUCTURAL_KEYWORDS):
                            structural_skips += 1
                            structural_skip_details.append(
                                {
                                    "sheet": sheet_name,
                                    "row": idx + 1,
                                    "content": " | ".join(
                                        [str(c) for c in non_empty][:8]
                                    ),
                                    "reason": "Metadata / Header row (expected)",
                                }
                            )
                            continue

                        # --- Structural skip: row has NO numbers at all ---
                        has_any_number = any(
                            c.replace(",", "")
                            .replace(".", "", 1)
                            .replace("-", "", 1)
                            .strip()
                            .isdigit()
                            for c in non_empty
                            if c.replace(",", "")
                            .replace(".", "", 1)
                            .replace("-", "", 1)
                            .strip()
                        )
                        if not has_any_number:
                            structural_skips += 1
                            structural_skip_details.append(
                                {
                                    "sheet": sheet_name,
                                    "row": idx + 1,
                                    "content": " | ".join(
                                        [str(c) for c in non_empty][:8]
                                    ),
                                    "reason": "Section divider row — no numeric data (expected)",
                                }
                            )
                            continue

                        # === Extract data from row ===
                        size_label = None
                        differential = None
                        final_rate = None
                        extra_note = ""
                        all_numbers = []

                        for cell in row_list:
                            if not cell or not isinstance(cell, str):
                                continue

                            c_lower = cell.lower()

                            # Size label detection
                            if (
                                any(k in c_lower for k in SIZE_KEYWORDS)
                                and len(cell) < 75
                            ):
                                if size_label is None or len(cell) > len(size_label):
                                    size_label = cell.strip()

                            # Collect all numbers
                            cleaned = (
                                cell.replace(",", "")
                                .replace("₹", "")
                                .replace(" ", "")
                                .replace("TO", "-")
                                .replace("–", "-")
                                .strip()
                            )
                            is_numeric = (
                                cleaned.lstrip("-").replace(".", "", 1).isdigit()
                                and cleaned.count("-") <= 1
                                and len(cleaned) > 0
                            )
                            if is_numeric:
                                try:
                                    all_numbers.append(Decimal(cleaned))
                                except Exception:
                                    pass

                            # Extra note
                            if any(
                                w in c_lower
                                for w in ["extra", "ask", "fresh", "special"]
                            ):
                                extra_note = cell.strip()

                        # Assign numbers by magnitude
                        for num in all_numbers:
                            if num >= 40000:
                                final_rate = num
                            elif 0 < num < 25000:
                                differential = num

                        # ✅ CARRY FORWARD: fill nulls from previous row values
                        if size_label is None:
                            size_label = prev_size_label
                        if final_rate is None:
                            final_rate = prev_final_rate
                        if differential is None:
                            differential = prev_differential
                        if not extra_note:
                            extra_note = prev_extra_note

                        # ✅ UPDATE carry-forward state only when we got a fresh value
                        if size_label is not None:
                            prev_size_label = size_label
                        if final_rate is not None:
                            prev_final_rate = final_rate
                        if differential is not None:
                            prev_differential = differential
                        if extra_note:
                            prev_extra_note = extra_note

                        # === Process valid size + rate pair ===
                        if size_label and final_rate is not None:

                            sheet_lower = sheet_name.lower()
                            text_lower = full_text

                            if (
                                "pipe" in sheet_lower
                                or "od" in size_label.lower()
                                or '"' in size_label
                            ):
                                product_type = ProductType.objects.filter(
                                    name__icontains="Pipe"
                                ).first()
                            elif "flat" in text_lower or (
                                "x" in size_label.lower()
                                and "od" not in size_label.lower()
                            ):
                                product_type = ProductType.objects.filter(
                                    name__icontains="Flat"
                                ).first()
                            elif "angle" in text_lower or "angle" in size_label.lower():
                                product_type = ProductType.objects.filter(
                                    name__icontains="Angle"
                                ).first()
                            elif "channel" in text_lower:
                                product_type = ProductType.objects.filter(
                                    name__icontains="Channel"
                                ).first()
                            else:
                                product_type = ProductType.objects.filter(
                                    name__icontains=sheet_name
                                ).first()

                            if not product_type:
                                product_name = sheet_name.strip() or "Auto Imported"
                                product_type = ProductType.objects.filter(
                                    name__iexact=product_name
                                ).first()

                                if not product_type:
                                    category = Category.objects.filter(
                                        is_active=True
                                    ).first()
                                    if not category:
                                        category = Category.objects.create(
                                            name="Mild Steel",
                                            slug="mild-steel",
                                            is_active=True,
                                        )
                                    product_type = ProductType.objects.create(
                                        category=category,
                                        name=product_name,
                                        description="Auto-created from Excel upload",
                                        is_active=True,
                                    )

                            variant, created = ProductVariant.objects.update_or_create(
                                product_type=product_type,
                                size_label=size_label,
                                defaults={
                                    "differential": differential,
                                    "final_rate": final_rate,
                                    "extra_note": extra_note[:255],
                                    "is_active": True,
                                },
                            )

                            if not created and variant.final_rate != final_rate:
                                PriceHistory.objects.create(
                                    variant=variant,
                                    old_rate=variant.final_rate,
                                    new_rate=final_rate,
                                    note=f"Updated via Excel on {today}",
                                )

                            updated_count += 1

                        else:
                            reason = (
                                "Missing Size"
                                if not size_label
                                else "Missing Rate (no number ≥ 40,000)"
                            )
                            data_failures += 1
                            data_failure_details.append(
                                {
                                    "sheet": sheet_name,
                                    "row": idx + 1,
                                    "content": " | ".join(
                                        [str(c) for c in non_empty][:7]
                                    ),
                                    "size_found": bool(size_label),
                                    "rate_found": bool(final_rate),
                                    "numbers_found": [str(n) for n in all_numbers],
                                    "reason": reason,
                                }
                            )

                    except Exception as row_err:
                        errors.append(f"Row {idx + 1} in {sheet_name}: {str(row_err)}")
                        data_failures += 1
                        continue

        response = {
            "success": True,
            "message": f"Successfully updated {updated_count} product variants.",
            "updated": updated_count,
            "skipped": data_failures,
            "structural_skips": structural_skips,
            "file_name": excel_file.name,
            "date": today.strftime("%Y-%m-%d"),
        }

        if data_failure_details:
            response["skipped_details"] = data_failure_details[:40]
        if structural_skip_details:
            response["structural_skip_details"] = structural_skip_details[:20]
        if errors:
            response["errors"] = errors[:10]

        return Response(response)

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "hint": "Try re-saving the Excel file as .xlsx (strict) before uploading.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ====================== ADMIN API ENDPOINTS ======================


# Categories
class AdminCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()


# Product Types
class AdminProductTypeListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductTypeSerializer
    queryset = ProductType.objects.all()


class AdminProductTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductTypeSerializer
    queryset = ProductType.objects.all()


# Product Variants (Main pricing items)
class AdminProductVariantListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductVariantSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = ProductVariant.objects.all().select_related(
            "product_type", "product_type__category"
        )
        type_slug = self.request.query_params.get("type")
        if type_slug:
            qs = qs.filter(product_type__slug=type_slug)
        return qs


class AdminProductVariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductVariantSerializer
    queryset = ProductVariant.objects.all()


# Price History
class PriceHistoryListView(generics.ListAPIView):
    serializer_class = PriceHistorySerializer

    def get_queryset(self):
        variant_id = self.kwargs.get("variant_id")
        return PriceHistory.objects.filter(variant_id=variant_id)


# Contact Inquiries
class AdminInquiryListView(generics.ListAPIView):
    serializer_class = ContactInquirySerializer

    def get_queryset(self):
        qs = ContactInquiry.objects.all()
        status_filter = self.request.query_params.get("status")
        if status_filter == "unread":
            qs = qs.filter(is_read=False)
        elif status_filter == "read":
            qs = qs.filter(is_read=True)
        return qs


# ==================== NEW: Create Contact Inquiry (POST) ====================
@csrf_exempt
@api_view(["GET", "POST"])
def create_inquiry(request):
    if request.method == "GET":
        """Return form metadata for frontend"""
        serializer = ContactInquirySerializer()

        # Get field information safely
        fields_info = {}
        for field_name, field in serializer.fields.items():
            fields_info[field_name] = {
                "type": field.__class__.__name__,
                "required": field.required,
                "read_only": field.read_only,
                "allow_null": getattr(field, "allow_null", False),
                "allow_blank": getattr(field, "allow_blank", False),
            }

        return Response(
            {
                "success": True,
                "message": "Inquiry creation form schema",
                "fields": fields_info,
                "product_interests": list(
                    ProductType.objects.filter(is_active=True)
                    .values_list("name", flat=True)
                    .order_by("name")
                ),  # Helpful for dropdown
            }
        )

    # ====================== POST Request ======================
    serializer = ContactInquirySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Your inquiry has been submitted successfully!",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {
            "success": False,
            "message": "Please correct the errors below.",
            "errors": serializer.errors,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@csrf_exempt
@api_view(["PATCH"])
def mark_inquiry_read(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    inquiry.is_read = True
    inquiry.save()
    return Response({"success": True, "message": "Inquiry marked as read"})


@csrf_exempt
@api_view(["DELETE"])
def delete_inquiry(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    inquiry.delete()
    return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)


# Dashboard Stats
@api_view(["GET"])
def dashboard_stats(request):
    return Response(
        {
            "total_categories": Category.objects.count(),
            "active_categories": Category.objects.filter(is_active=True).count(),
            "total_product_types": ProductType.objects.count(),
            "active_product_types": ProductType.objects.filter(is_active=True).count(),
            "total_variants": ProductVariant.objects.count(),
            "active_variants": ProductVariant.objects.filter(is_active=True).count(),
            "total_inquiries": ContactInquiry.objects.count(),
            "unread_inquiries": ContactInquiry.objects.filter(is_read=False).count(),
        }
    )


class PublicProductVariantListView(generics.ListAPIView):
    """GET /products/?category=<slug>   OR   /api/product-variants/?category=<slug>"""

    serializer_class = ProductVariantSerializer

    def get_queryset(self):
        qs = ProductVariant.objects.filter(is_active=True).select_related(
            "product_type", "product_type__category"
        )

        category_slug = self.request.query_params.get("category")
        type_slug = self.request.query_params.get("type")

        if category_slug:
            qs = qs.filter(product_type__category__slug=category_slug)
        elif type_slug:  # keep backward compatibility
            qs = qs.filter(product_type__slug=type_slug)

        return qs


@csrf_exempt
@api_view(["GET"])
def public_product_interest_list(request):
    """
    Returns list of all active ProductType names for the contact form dropdown.
    Used by frontend to populate "Product Interest" select box.
    """
    product_types = (
        ProductType.objects.filter(is_active=True)
        .values_list("name", flat=True)
        .order_by("name")
    )
    return Response(list(product_types))
