from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from service.views import (
    #class based views,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    SendOTPAPIView,
    VerifyOTPAPIView,
    ServiceView,
    ServiceDetailView,
    SendTechnicianOTPAPIView,
    VerifyTechnicianOTPAPIView,
    RequestsView,
    WasteCollectionAPIView,
    UserAPIView,
    AddressesAPIView,
    AddressDetailAPIView,
    
    #function based views,
    get_devices,
    get_categories,
    get_brands_by_category,
    get_models_by_brand,
    add_brands,
    add_models,
    delete_service,
    
    
    
    #templates
)


router = DefaultRouter()
router.register(r'tech/requests', RequestsView, basename='request')




urlpatterns = [
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    #user_service
    path('send-otp/', SendOTPAPIView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify'),
    path('service/', ServiceView.as_view(), name='service_request'),
    path('service/<int:pk>/', ServiceDetailView.as_view(), name='service_request_detail'),
    path('devices/', get_devices, name='get_devices'),
    path("categories/", get_categories),
    path('brands/<str:category_name>/',get_brands_by_category),
    path('models/<str:brand_name>/',get_models_by_brand),
    path('user/', UserAPIView.as_view(),),
    path('delete/<int:pk>/', delete_service, name='delete_service'),
    path('addresses/',AddressesAPIView.as_view(), name='addresses'),
    path('addresses/<int:pk>/',AddressesAPIView.as_view(), name='delete_addresses'),
    #user_waste
    path('waste/', WasteCollectionAPIView.as_view(), name='waste_collection'),
    #technician
    path('tech/send-otp/', SendTechnicianOTPAPIView.as_view(), name='send_technician_otp'),
    path('tech/verify-otp/', VerifyTechnicianOTPAPIView.as_view(), name='verify_technician_otp'),
    path('tech/service/<int:pk>/', ServiceDetailView.as_view(), name='service_request_detail'),
    path('tech/addresses/<int:pk>/',AddressDetailAPIView.as_view(), name='delete_addresses'),
    
    # path('tech/requests/', RequestsView.as_view(), name='technician_requests'),
    
]+ router.urls




# Serve media files during development

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)