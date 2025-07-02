from django.contrib import admin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from service.models import (
    Profile, PhoneOTP, Technician,
    ServiceRequest, Device, Category,
    Brand, DeviceModel,
    WasteCollection,
    Address
)

admin.site.unregister(Group)  # Unregister the default Group model
@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ("user", "name")
    search_fields = ("user__username", "name")

# @admin.register(PhoneOTP)
# class PhoneOTPAdmin(ModelAdmin):
#     list_display = ("phone_number", "otp", "is_verified", "created_at", "is_expired")
#     list_filter = ("is_verified",)
#     search_fields = ("phone_number",)

@admin.register(Technician)
class TechnicianAdmin(ModelAdmin):
    list_display = ("user", "name", "is_active", "is_verified")
    list_filter = ("is_active", "is_verified")
    search_fields = ("user__username", "name")

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)

@admin.register(DeviceModel)
class DeviceModelAdmin(ModelAdmin):
    list_display = ("name", "brand")
    list_filter = ("brand",)
    search_fields = ("name",)

# @admin.register(Device)
# class DeviceAdmin(ModelAdmin):
#     list_display = ("name", "brand")
#     list_filter = ("brand",)
#     search_fields = ("name",)

@admin.register(ServiceRequest)
class ServiceRequestAdmin(ModelAdmin):
    list_display = ("id", "profile", "technician", "status", "completed", "created_at", "total")
    list_filter = ("status", "completed", "created_at")
    search_fields = ("profile__user__username", "technician__user__username", "location", "description")
    filter_horizontal = ("devices",)  # For many-to-many widget


@admin.register(WasteCollection)
class WasteCollectionAdmin(ModelAdmin):
    list_display = ("id", "profile", "address", "status", "completed")
    list_filter = ("status", "id")
    # search_fields = ("profile__user__username", "technician__user__username", "location")

@admin.register(Address)
class AddressManagement(ModelAdmin):
    list_display = ("id", "profile", "location", "address", "houseflat", "landmark")
    list_filter = ("profile",)