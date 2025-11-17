"""
Path: bookmyadvocate/main/models.py
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('advocate', 'Advocate'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active_advocate = models.BooleanField(default=False)



class AdvocateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='advocate_profile')
    specialization = models.CharField(max_length=150, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)

class AdvocateRegistrationPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=200, null=True)
    razorpay_payment_id = models.CharField(max_length=200, null=True)
    razorpay_signature = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')

class Booking(models.Model):
    STATUS = [('pending','Pending'),('accepted','Accepted'),('rejected','Rejected')]
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_bookings')
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advocate_bookings')
    date = models.DateField()
    time = models.TimeField()
    purpose = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    meeting_link = models.URLField(blank=True)
