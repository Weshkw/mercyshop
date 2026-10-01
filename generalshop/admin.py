from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import (
    CustomUser,
    FeaturedVideo,
    InventoryProducts,
    MoreImages,
    Order,
    OrderedProduct,
    OtherPettyCosts,
    PettyCosts,
)


class CustomUserCreationForm(BaseUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["id_number", "first_name", "middle_name", "surname", "phone_number"]


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ["id_number", "get_full_name", "phone_number", "is_staff"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    fieldsets = [
        (None, {"fields": ["id_number", "password"]}),
        ("Personal info", {"fields": ["first_name", "middle_name", "surname", "phone_number"]}),
        (
            "Permissions",
            {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]},
        ),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": [
                    "id_number",
                    "first_name",
                    "middle_name",
                    "surname",
                    "phone_number",
                    "password1",
                    "password2",
                ],
            },
        ),
    ]
    search_fields = ["id_number", "first_name", "middle_name", "surname", "phone_number"]
    ordering = ["id_number"]


class MoreImagesInline(admin.TabularInline):
    model = MoreImages
    extra = 1


@admin.register(InventoryProducts)
class InventoryProductsAdmin(admin.ModelAdmin):
    list_display = ["product_name", "selling_price", "unit_amount", "unit_type", "date_updated"]
    search_fields = ["product_name", "description"]
    inlines = [MoreImagesInline]


@admin.register(FeaturedVideo)
class FeaturedVideoAdmin(admin.ModelAdmin):
    list_display = ["video"]


class OtherPettyCostsInline(admin.TabularInline):
    model = OtherPettyCosts
    extra = 0


@admin.register(PettyCosts)
class PettyCostsAdmin(admin.ModelAdmin):
    list_display = [
        "activity",
        "employee",
        "transport_cost",
        "lunch_cost",
        "airtime_cost",
        "date_created",
    ]
    list_filter = ["date_created"]
    list_select_related = ["employee"]
    inlines = [OtherPettyCostsInline]


class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    extra = 0
    autocomplete_fields = ["product"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["__str__", "complete", "date_ordered"]
    list_filter = ["complete"]
    inlines = [OrderedProductInline]
