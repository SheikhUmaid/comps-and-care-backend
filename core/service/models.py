from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
# Create your models here.

class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5) 

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="New User")
    # email = models.EmailField(max_length=255, unique=True, blank=True, null=True),
    dp = models.ImageField(upload_to='profile_pics/', default='default.jpg', blank=True, null=True)
    

    def __str__(self):
        return f"{self.name}'s profile"

class Technician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dp = models.ImageField(upload_to='technician_pics/', default='default.jpg', blank=True, null=True)
    # email = models.EmailField(max_length=255, unique=True, blank=True, null=True),
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username}'s technician profile"
    
    

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name
    

class DeviceModel(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name
    
class Device(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name + f" - {self.price}"



class Address(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    houseflat = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"{self.address} - {self.profile.user.username}"



class ServiceRequest(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    devices = models.ManyToManyField(DeviceModel, blank=True)
    description = models.TextField()
    date = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='pending')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    urgent_request = models.BooleanField(default=False);
    emergency_request = models.BooleanField(default=False)
    def __str__(self):
        return f"Service Request {self.id} by {self.profile.user.username}"
    
    
    
class WasteCollection(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    date = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='pending')
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Waste Collection Request {self.id} by {self.profile.user.username}"
    