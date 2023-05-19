from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import inlineformset_factory
from .models import CustomUser,InventoryProducts,MoreImages, PettyCosts,OtherPettyCosts,OrderedProduct,Order
from django.db import models



class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id_number', 'get_full_name', 'phone_number', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('id_number', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'middle_name', 'surname', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id_number', 'password1', 'password2'),
        }),
    )
    search_fields = ('id_number', 'first_name', 'middle_name', 'surname', 'phone_number')
    ordering = ('id_number',)  # Change this to refer to a valid field in your CustomUser model



class MoreImagesInline(admin.StackedInline):
    model=MoreImages
    extra= 1

@admin.register(InventoryProducts)
class InventoryProductsAdmin(admin.ModelAdmin):
    list_display = ('product_name',)
    inlines = [MoreImagesInline,]


MultipleImageFormSet = inlineformset_factory(InventoryProducts, MoreImages, fields=('more_images',), extra=1)



admin.site.register(CustomUser, CustomUserAdmin)



# Handles the petty costs of the business associated with each user


class OtherPettyCostsInline(admin.StackedInline):
    model = OtherPettyCosts
    
    max_num = 1

@admin.register(PettyCosts)
class PettyCostsAdmin(admin.ModelAdmin):
    list_display = ['activity', 'transport_cost', 'lunch_cost', 'airtime_cost', 'date_created']
    # Customize other options and fields as needed

    inlines = [OtherPettyCostsInline,]


admin.site.register(OrderedProduct)
admin.site.register(Order)



