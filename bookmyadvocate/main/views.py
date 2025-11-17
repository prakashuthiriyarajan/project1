from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Booking, AdvocateProfile
from django.db.models import Q


# -------------------------
# HOME PAGE
# -------------------------
def home(request):
    return render(request, "home.html")


# -------------------------
# CLIENT REGISTRATION
# -------------------------
def register_client(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, "register_client.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="client",
        )
        messages.success(request, "Registration successful! Please login.")
        return redirect("login")

    return render(request, "register_client.html")


# -------------------------
# ADVOCATE REGISTRATION
# -------------------------
def register_advocate(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, "register_advocate.html")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="advocate",
            is_active_advocate=True
        )
        
        # Create advocate profile
        AdvocateProfile.objects.create(user=user)
        
        messages.success(request, "Registration successful! Please login.")
        return redirect("login")

    return render(request, "register_advocate.html")


# -------------------------
# LOGIN
# -------------------------
def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            if user.role == "client":
                return redirect("client_dashboard")
            elif user.role == "advocate":
                return redirect("advocate_dashboard")
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, "login.html")


# -------------------------
# LOGOUT
# -------------------------
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("login")


# -------------------------
# CLIENT DASHBOARD
# -------------------------
@login_required
def client_dashboard(request):
    if request.user.role != 'client':
        messages.error(request, "Access denied!")
        return redirect("home")
    
    bookings = Booking.objects.filter(client=request.user).order_by('-created_at')
    
    context = {
        'bookings': bookings
    }
    return render(request, "client_dashboard.html", context)


# -------------------------
# ADVOCATE DASHBOARD
# -------------------------
@login_required
def advocate_dashboard(request):
    if request.user.role != 'advocate':
        messages.error(request, "Access denied!")
        return redirect("home")
    
    return render(request, "advocate_dashboard.html")


# -------------------------
# SEARCH ADVOCATES
# -------------------------
def search_advocates(request):
    """
    View to search and display advocates
    """
    query = request.GET.get('q', '')
    
    if query:
        # Search for advocates by username, email, first_name, or last_name
        advocates = User.objects.filter(
            Q(role='advocate') &
            Q(is_active_advocate=True) &
            (Q(username__icontains=query) |
             Q(email__icontains=query) |
             Q(first_name__icontains=query) |
             Q(last_name__icontains=query))
        )
    else:
        # Show all advocates if no search query
        advocates = User.objects.filter(role='advocate', is_active_advocate=True)
    
    context = {
        'advocates': advocates,
        'query': query
    }
    return render(request, 'search_advocates.html', context)


# -------------------------
# PLACEHOLDER VIEWS (to be implemented)
# -------------------------
@login_required
def edit_advocate_profile(request):
    """Placeholder for advocate profile editing"""
    messages.info(request, "Profile editing feature coming soon!")
    return redirect("advocate_dashboard")


@login_required
def booking_detail(request, booking_id):
    """Placeholder for booking detail view"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has access to this booking
    if request.user != booking.client and request.user != booking.advocate:
        messages.error(request, "Access denied!")
        return redirect("home")
    
    messages.info(request, "Booking detail page coming soon!")
    
    if request.user.role == 'client':
        return redirect("client_dashboard")
    else:
        return redirect("advocate_dashboard")