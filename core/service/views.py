from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.viewsets import ViewSet
from service.utils import generate_otp, send_otp_via_sms, send_otp_via_email
from service.models import Profile
from service.models import PhoneOTP
from service.models import ServiceRequest
from service.models import Technician
from service.models import Device
from service.models import Brand
from service.models import Category
from service.models import DeviceModel
from service.models import WasteCollection
from service.models import Address
from service.serializers import SendOTPSerializer
from service.serializers import VerifyOTPSerializer
from service.serializers import ServiceRequestSerializer
from service.serializers import ProfileSerializer
from service.serializers import TechnicianSerializer
from service.serializers import CategorySerializer
from service.serializers import DeviceSerializer
from service.serializers import BrandSerializer
from service.serializers import WasteCollectionSerializer
from service.serializers import AddressSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
import pandas as pd

logger = logging.getLogger(__name__)
laptops = pd.read_csv("laptops.csv")

class CustomTokenRefreshView(TokenRefreshView):
    pass  # Uses default behavior

class CustomTokenObtainPairView(TokenObtainPairView):
    pass  # Uses default behavior

class SendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(__name__)
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            email = serializer.validated_data['email']
            otp = generate_otp()
            # send_otp_via_sms(phone_number, otp)
            send_otp_via_email(email, otp);
            PhoneOTP.objects.update_or_create(
                phone_number=phone_number,
                # email=email,
                defaults={'otp': otp, 'created_at': timezone.now(), 'is_verified': False,'email': email}
            )
            logger.info(f"OTP {otp} sent to {phone_number}")
            print(f"OTP {otp} sent to {phone_number}")
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAPIView(APIView):
    
    
    MASTER_OTP = "0102"  # Master OTP for bypassing (use only in dev/testing)

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.validated_data['otp']

            # Master OTP check
            if otp == self.MASTER_OTP:
                user, created = User.objects.get_or_create(username=phone_number)
                if created:
                    print("User created via master OTP:", user)
                    user.set_unusable_password()
                    user.save()

                profile, created = Profile.objects.get_or_create(user=user)
                profile.save()

                access_token = AccessToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)

                return Response({
                    "access_token": str(access_token),
                    "refresh_token": str(refresh_token),
                    "message": "Logged in using master OTP"
                }, status=200)

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.validated_data['otp']
            try:
                otp_record = PhoneOTP.objects.get(phone_number=phone_number, otp=otp)
                
            except PhoneOTP.DoesNotExist:
                return Response({"error": "Invalid OTP"}, status=400)
            
            if otp_record.is_verified:
                otp_record.delete()
                return Response({"error": "OTP already used"}, status=400)
            
            if otp_record.is_expired():
                otp_record.delete()
                return Response({"error": "OTP has expired"}, status=400)

            
            user, created = User.objects.get_or_create(username=phone_number)
            
            if created:
                print("User created:", user)
                user.set_unusable_password()
                user.save()
            
            
            profile, created = Profile.objects.get_or_create(user=user)
            profile.save()
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            otp_record.delete()
            return Response({"access_token": str(access_token), "refresh_token": str(refresh_token)}, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
    def get(self, request):
        print("ServiceView get method called")
        print(request.user)
        user = get_object_or_404(User, id=request.user.id)
        print(user)
        profile = get_object_or_404(Profile, user=user)
        service_requests = ServiceRequest.objects.filter(profile=profile).order_by('-created_at')
        serializer = ServiceRequestSerializer(service_requests, many=True)
        return Response(serializer.data, status=200)
    
    
    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        print(user)
        profile = get_object_or_404(Profile, user=user)
        serializer = ServiceRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ServiceDetailView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    
    
    def get(self, request, pk):
        service_request = get_object_or_404(ServiceRequest, pk=pk,)
        serializer = ServiceRequestSerializer(service_request)
        return Response(serializer.data, status=200)

    def delete(self, request, pk):
        user = get_object_or_404(User, id=request.user.id)
        profile = get_object_or_404(Profile, user=user)
        service_request = get_object_or_404(ServiceRequest, pk=pk, profile=profile)
        service_request.delete()
        return Response(status=204)

class SendTechnicianOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            user = User.objects.filter(username=phone_number).first()
            if user is None:
                return Response({"error": "Technician does not exist"}, status=400)
                # send_otp_via_sms(phone_number, otp)
                
            tech = Technician.objects.filter(user=user).first()
            if tech is not None:    
                otp = generate_otp()
                
                PhoneOTP.objects.update_or_create(
                    phone_number=phone_number,
                    defaults={'otp': otp, 'created_at': timezone.now(), 'is_verified': False}
                )
                logger.info(f"OTP {otp} sent to {phone_number}")
                print(f"OTP {otp} sent to {phone_number}")
                return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
            if tech is None:
                return Response({"error": "Technician does not exist"}, status=400)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyTechnicianOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.validated_data['otp']
            try:
                otp_record = PhoneOTP.objects.get(phone_number=phone_number, otp=otp)
            except PhoneOTP.DoesNotExist:
                return Response({"error": "Invalid OTP"}, status=400)
            
            if otp_record.is_verified:
                otp_record.delete()
                return Response({"error": "OTP already used"}, status=400)
            
            if otp_record.is_expired():
                otp_record.delete()
                return Response({"error": "OTP has expired"}, status=400)

            user = User.objects.filter(username=phone_number).first()
            
            if user is None:
                
                return Response({"error": "Technician does not exist"}, status=400)
                
            tech = Technician.objects.filter(user=user).first()
            if tech is not None:    
                print("Technician created:", user)
                access_token = AccessToken.for_user(user)
                refresh_token = RefreshToken.for_user(user)
                return Response({
                    "access_token": str(access_token),
                    "refresh_token": str(refresh_token)}, status=status.HTTP_200_OK)
            
            otp_record.delete()
            return Response({"message": "Technician verified successfully."}, status=201)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestsView(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def list(self, request):
        requests = ServiceRequest.objects.all().order_by('-created_at')
        serializer = ServiceRequestSerializer(requests, many=True)
        return Response(serializer.data, status=200)
    
    
    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        queryset = ServiceRequest.objects.filter(technician=None).order_by('-created_at')
        serializer = ServiceRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def mine(self, request):
        queryset = ServiceRequest.objects.filter(technician=request.user.technician, completed=False).order_by('-created_at')
        serializer = ServiceRequestSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        queryset = ServiceRequest.objects.filter(technician=request.user.technician, completed=True).order_by('-created_at')
        serializer = ServiceRequestSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_completed(self, request):
        service_request_id = request.data.get('service_request_id')
        if not service_request_id:
            return Response({"error": "Service request ID is required"}, status=400)
        
        try:
            service_request = ServiceRequest.objects.get(pk=service_request_id, technician=request.user.technician)
            service_request.completed = True
            service_request.save()
            serializer = ServiceRequestSerializer(service_request)
            return Response(serializer.data, status=200)
        except ServiceRequest.DoesNotExist:
            return Response({"error": "Service request not found"}, status=404)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        user = get_object_or_404(User, id=request.user.id)
        technician = get_object_or_404(Technician, user=user)
        service_request.technician = technician
        service_request.teaken = True
        service_request.save()
        serializer = ServiceRequestSerializer(service_request)
        return Response(serializer.data, status=200)
    
    @action(detail=True, methods=['post'])
    def getbyid(self, request, pk=None):
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        serializer = ServiceRequestSerializer(service_request)
        return Response(serializer.data, status=200)
    
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        status = request.data.get('status')
        if status:
            service_request.status = status
            service_request.save()
            serializer = ServiceRequestSerializer(service_request)
            return Response(serializer.data, status=200)
        return Response({"error": "Status not provided"}, status=400)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        service_request.completed = True
        service_request.save()
        serializer = ServiceRequestSerializer(service_request)
        return Response(serializer.data, status=200)
    
    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        service_request.delete()
        return Response(status=204)

class AddressesAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    
    def get(self, request, pk=None):
        user = get_object_or_404(User, id=request.user.id)
        profile = get_object_or_404(Profile, user=user)

        if pk:
            address = get_object_or_404(Address, pk=pk, profile=profile)
            serializer = AddressSerializer(address)
        else:
            addresses = Address.objects.filter(profile=profile).order_by('-id')
            serializer = AddressSerializer(addresses, many=True)

        return Response(serializer.data, status=200)

    
    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        profile = get_object_or_404(Profile, user = user)
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            address = serializer.save(profile=profile)
            return Response(AddressSerializer(address).data, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, pk):
        user = get_object_or_404(User, id=request.user.id)
        profile = get_object_or_404(Profile, user=user)
        address = get_object_or_404(Address, pk=pk, profile=profile)
        address.delete()
        return Response({"message": "Address deleted successfully"}, status=204)

class AddressDetailAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        address = get_object_or_404(Address, pk=pk)
        serializer = AddressSerializer(address)
        return Response(serializer.data, status=200)

    def put(self, request, pk):
        user = get_object_or_404(User, id=request.user.id)
        profile = get_object_or_404(Profile, user=user)
        address = get_object_or_404(Address, pk=pk, profile=profile)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

class UserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        print("UserAPIView get method called")
        user = get_object_or_404(User, id=request.user.id)
        serializer = ProfileSerializer(user.profile)
        print(serializer.data)
        return Response(serializer.data, status=200)

    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = ProfileSerializer(user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    def delete(self, request):
        user = get_object_or_404(User, id=request.user.id)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=204)

class WasteCollectionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
    def get(self, request):
        print("Waste get method called")
        print(request.user)
        user = get_object_or_404(User, id=request.user.id)
        print(user)
        profile = get_object_or_404(Profile, user=user)
        service_requests = WasteCollection.objects.filter(profile=profile).order_by('-id')
        serializer = WasteCollectionSerializer(service_requests, many=True)
        return Response(serializer.data, status=200)
    
    
    def post(self, request):
        user = get_object_or_404(User, id=request.user.id)
        print(user)
        profile = get_object_or_404(Profile, user=user)
        serializer = WasteCollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_devices(request):
    devices = Device.objects.all().order_by('name')
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data, status=200)

@api_view(['DELETE'])
def delete_service(request, pk):
    try:
        service = ServiceRequest.objects.get(pk=pk)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ServiceRequest.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def mark_completed(request, pk):
    try:
        service = ServiceRequest.objects.get(pk=pk)
        service.is_completed = True
        service.save()
        # Notify group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"service_{pk}",
            {
                'type': 'send_service_complete',
            }
        )
        return Response({'status': 'completed'})
    except ServiceRequest.DoesNotExist:
        return Response({'error': 'Service not found'}, status=404)

@api_view(['GET'])
def get_categories(request):
    cats = Category.objects.all();
    serializer = CategorySerializer(cats, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def get_brands_by_category(request, category_name):
    search_query = request.query_params.get('search', None)
    # Filter by category name
    brands = Brand.objects.filter(category__name__iexact=category_name)
    if search_query:
        brands = brands.filter(name__icontains=search_query)

    serializer = BrandSerializer(brands, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def get_models_by_brand(request, brand_name):
    search_query = request.query_params.get('search', None)
    models = DeviceModel.objects.filter(brand__name__iexact=brand_name)
    if search_query:
        models = DeviceModel.objects.filter(name__icontains=search_query)
    serializer = DeviceSerializer(models, many=True)
    return Response(serializer.data, status=200)

def add_brands(request):
    # laptops['brand'].unique().tolist()
    lap = Category.objects.get(pk=1)
    for i in laptops['brand'].unique().tolist():
        a = Brand.objects.create(name=str(i), category=lap )
        a.save()
        print(i)
    return HttpResponse("<h1>Check</h1>")

def add_models(request):
    for i in range(len(laptops)):
        brand_name = laptops.iloc[i]['brand']
        model_name = laptops.iloc[i]['Model']

        try:
            brand_obj = Brand.objects.get(name=brand_name)
            # Check if this model already exists to avoid duplicates
            if not DeviceModel.objects.filter(name=model_name, brand=brand_obj).exists():
                DeviceModel.objects.create(name=model_name, brand=brand_obj)
                print(f"✅ Created model '{model_name}' under brand '{brand_name}'")
        except Brand.DoesNotExist:
            print(f"❌ Brand '{brand_name}' not found in the database. Skipping.")

    return HttpResponse("<h1>Device Models Added</h1>")

def support(request, path):
    if path == 'about':
        return render(request, 'about.html')
    elif path == 'contact':
        return render(request, 'contact.html')
    elif path == 'terms':
        return render(request, 'terms.html')
    elif path == 'privacy':
        return render(request, 'privacy.html')
    elif path == 'faq':
        return render(request, 'faq.html')
    else:
        return HttpResponse("Page not found", status=404)
    return render(request, 'about.html')