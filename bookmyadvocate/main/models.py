"""
Path: bookmyadvocate/main/models.py
FIXED: Bar Council Number as unique identifier for advocates
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('advocate', 'Advocate'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active_advocate = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # ADDED: Bar Council Number for advocates (unique identifier)
    bar_council_number = models.CharField(max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class AdvocateProfile(models.Model):
    SPECIALIZATION_CHOICES = [
        ('criminal', 'Criminal Law'),
        ('civil', 'Civil Law'),
        ('corporate', 'Corporate Law'),
        ('family', 'Family Law'),
        ('tax', 'Tax Law'),
        ('property', 'Property Law'),
        ('labor', 'Labor Law'),
        ('intellectual', 'Intellectual Property'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='advocate_profile')
    specialization = models.CharField(max_length=150, choices=SPECIALIZATION_CHOICES, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_cases = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_specialization_display()}"


class AdvocateRegistrationPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=200, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=200, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.payment_status}"


class Booking(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_bookings')
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advocate_bookings')
    date = models.DateField()
    time = models.TimeField()
    purpose = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    meeting_link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client.username} -> {self.advocate.username} on {self.date}"


class Document(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.booking}"


class Review(models.Model):
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client.username} rated {self.advocate.username} - {self.rating}/5"