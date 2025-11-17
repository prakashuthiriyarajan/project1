"""
Path: bookmyadvocate/main/admin.py
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AdvocateProfile, AdvocateRegistrationPayment, Booking

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (('Role',{'fields':('role','is_active_advocate')}),)

admin.site.register(User, UserAdmin)
admin.site.register(AdvocateProfile)
admin.site.register(AdvocateRegistrationPayment)
admin.site.register(Booking)
