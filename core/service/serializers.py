from rest_framework import serializers
from service.models import PhoneOTP, Profile, Technician, ServiceRequest, Device, Category, Brand, DeviceModel, WasteCollection, Address
from django.contrib.auth.models import User



class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)
    otp = serializers.CharField(max_length=6, required=True)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class BrandSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # instantiate it here

    class Meta:
        model = Brand
        fields = ['name', 'category']


        

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'name', 'price']
        read_only_fields = ['id']  # Make this field read-only

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', ]
        read_only_fields = ['id']  # Make this field read-only



class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    dp = serializers.ImageField(write_only=True, required=False)  # For uploading
    dp_url = serializers.SerializerMethodField(read_only=True)    # For returning media/profile_pics/file.jpg

    class Meta:
        model = Profile
        fields = ['id', 'user', 'name', 'dp', 'dp_url']
        read_only_fields = ['id']

    def get_dp_url(self, obj):
        if obj.dp:
            return f"media/{obj.dp.name}"
        return None

class TechnicianSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Technician
        fields = ['id', 'user',]
        read_only_fields = ['id']  # Make this field read-only

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'brand', 'name']
        read_only_fields = ['id']  # Make this field read-only


class ServiceRequestSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    technician = TechnicianSerializer(read_only=True)
    
    # Accept device IDs in input
    devices = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DeviceModel.objects.all()
    )

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'profile', 'technician', 'devices',
            'description','address',
            'date', 'status', 'completed',
            'created_at', 'updated_at', 'total','urgent_request', 'emergency_request'
        ]
        read_only_fields = ['id', 'profile', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['devices'] = DeviceSerializer(instance.devices.all(), many=True).data
        return data

    def run_validation(self, data=serializers.empty):
        """
        Override to silently drop unknown fields (like 'timeslot')
        """
        if isinstance(data, dict):
            allowed = set(self.fields)
            # Remove unknown fields
            data = {key: value for key, value in data.items() if key in allowed}
        return super().run_validation(data)






class WasteCollectionSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = WasteCollection
        fields = ['id', 'profile', 'date', 'address', 'status', 'completed']
        read_only_fields = ['id', 'profile']  # Make this field read-only

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['profile'] = ProfileSerializer(instance.profile).data
        return data


class AddressSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer(read_only=True)7
    class Meta:
        model = Address
        # fields = ['id', 'address', 'location', 'houseflat', 'landmark']
        exclude = ['profile']
        # read_only_fields = ['id']  # Make this field read-only
        # fields = ['id', 'address', 'location','houseflat', 'landmark','profile' ]
        # read_only_fields = ['id', 'profile']  # Make this field read-only

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['address'] = instance.address
        return data
