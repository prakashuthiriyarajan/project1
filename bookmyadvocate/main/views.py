"""
Path: bookmyadvocate/main/views.py
COMPLETE FIX - Role-based login + Email checking instead of username
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from .models import User, AdvocateProfile, Booking, Document, Review


# -------------------------
# HOME PAGE
# -------------------------
def home(request):
    advocates = User.objects.filter(role='advocate', is_active_advocate=True)[:6]
    return render(request, "home.html", {'advocates': advocates})


# -------------------------
# CLIENT REGISTRATION - FIXED
# -------------------------
def register_client(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("phone", "")

        # Validate required fields
        if not username or not email or not password:
            messages.error(request, "All fields except phone are required!")
            return render(request, "register_client.html")

        # FIXED: Check if EMAIL already exists (not username)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "register_client.html")

        # Create client user
        try:
            user = User.objects.create_user(
                username=email,  # Use email as username internally
                email=email,
                password=password,
                role="client",
                phone=phone
            )
            user.is_active = True
            user.save()
            
            messages.success(request, "Registration successful! Please login with your email.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, "register_client.html")

    return render(request, "register_client.html")


# -------------------------
# ADVOCATE REGISTRATION - FIXED
# -------------------------
def register_advocate(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        bar_council_number = request.POST.get("bar_council_number")
        password = request.POST.get("password")
        phone = request.POST.get("phone", "")

        # Validate required fields
        if not username or not email or not bar_council_number or not password:
            messages.error(request, "All fields except phone are required!")
            return render(request, "register_advocate.html")

        # FIXED: Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "register_advocate.html")
        
        # Check if bar council number already exists
        if User.objects.filter(bar_council_number=bar_council_number).exists():
            messages.error(request, "Bar Council Number already registered!")
            return render(request, "register_advocate.html")

        # Create advocate user
        try:
            user = User.objects.create_user(
                username=bar_council_number,  # Use bar council number as username internally
                email=email,
                password=password,
                role="advocate",
                phone=phone,
                bar_council_number=bar_council_number
            )
            user.is_active = True
            user.is_active_advocate = True
            user.save()
            
            # Create advocate profile
            AdvocateProfile.objects.create(user=user)
            
            messages.success(request, "Registration successful! Please login with your Bar Council Number.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return render(request, "register_advocate.html")

    return render(request, "register_advocate.html")


# -------------------------
# LOGIN - FIXED (Role-based)
# -------------------------
def user_login(request):
    if request.method == "POST":
        role = request.POST.get("role")  # 'client' or 'advocate'
        credential = request.POST.get("credential")  # email or bar_council_number
        password = request.POST.get("password")

        if not role or not credential or not password:
            messages.error(request, "All fields are required!")
            return render(request, "login.html")

        user = None

        try:
            if role == "client":
                # Client login with email
                try:
                    user_obj = User.objects.get(email=credential, role='client')
                    # Authenticate using the internal username (which is email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    messages.error(request, "No client found with this email!")
                    return render(request, "login.html")
                
            elif role == "advocate":
                # Advocate login with bar council number
                try:
                    user_obj = User.objects.get(bar_council_number=credential, role='advocate')
                    # Authenticate using the internal username (which is bar council number)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    messages.error(request, "No advocate found with this Bar Council Number!")
                    return render(request, "login.html")
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.email}!")
                
                if user.role == "client":
                    return redirect("client_dashboard")
                elif user.role == "advocate":
                    return redirect("advocate_dashboard")
            else:
                messages.error(request, "Invalid password!")
                
        except Exception as e:
            messages.error(request, f"Login failed: {str(e)}")

    return render(request, "login.html")


# -------------------------
# LOGOUT
# -------------------------
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("home")


# -------------------------
# CLIENT DASHBOARD
# -------------------------
@login_required
def client_dashboard(request):
    if request.user.role != 'client':
        return redirect('advocate_dashboard')
    
    bookings = Booking.objects.filter(client=request.user).order_by('-created_at')
    return render(request, "client_dashboard.html", {'bookings': bookings})


# -------------------------
# ADVOCATE DASHBOARD
# -------------------------
# -------------------------
# ADVOCATE DASHBOARD
# -------------------------
@login_required
def advocate_dashboard(request):
    if request.user.role != 'advocate':
        messages.error(request, "Access denied!")
        return redirect("home")
    
    # Get advocate's bookings
    bookings = Booking.objects.filter(advocate=request.user).order_by('-created_at')
    
    # Get advocate's profile
    profile = request.user.advocate_profile
    
    context = {
        'bookings': bookings,
        'profile': profile
    }
    return render(request, "advocate_dashboard.html", context)


# -------------------------
# ADVOCATE PROFILE EDIT
# -------------------------
@login_required
def edit_advocate_profile(request):
    if request.user.role != 'advocate':
        messages.error(request, "Only advocates can access this page!")
        return redirect('home')
    
    profile, created = AdvocateProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        specialization = request.POST.get('specialization')
        experience_years = request.POST.get('experience_years', 0)
        location = request.POST.get('location', '')
        bio = request.POST.get('bio', '')
        consultation_fee = request.POST.get('consultation_fee', 500)
        
        profile.specialization = specialization
        profile.experience_years = experience_years
        profile.location = location
        profile.bio = bio
        profile.consultation_fee = consultation_fee
        profile.save()
        
        request.user.is_active_advocate = True
        request.user.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('advocate_dashboard')
    
    return render(request, 'edit_advocate_profile.html', {'profile': profile})


# -------------------------
# SEARCH ADVOCATES
# -------------------------
def search_advocates(request):
    query = request.GET.get('q', '')
    
    if query:
        advocates = User.objects.filter(
            Q(role='advocate') &
            Q(is_active_advocate=True) &
            (Q(email__icontains=query) |
             Q(advocate_profile__location__icontains=query) |
             Q(bar_council_number__icontains=query))
        ).distinct()
    else:
        advocates = User.objects.filter(role='advocate', is_active_advocate=True)
    
    return render(request, 'search_advocates.html', {
        'advocates': advocates,
        'query': query
    })


# -------------------------
# ADVOCATE DETAIL
# -------------------------
def advocate_detail(request, advocate_id):
    advocate = get_object_or_404(User, id=advocate_id, role='advocate')
    profile = get_object_or_404(AdvocateProfile, user=advocate)
    reviews = Review.objects.filter(advocate=advocate).order_by('-created_at')
    
    return render(request, 'advocate_detail.html', {
        'advocate': advocate,
        'profile': profile,
        'reviews': reviews
    })


# -------------------------
# BOOK CONSULTATION
# -------------------------
@login_required
def book_consultation(request, advocate_id):
    if request.user.role != 'client':
        messages.error(request, "Only clients can book consultations")
        return redirect('home')
    
    advocate = get_object_or_404(User, id=advocate_id, role='advocate')
    
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        purpose = request.POST.get('purpose')
        notes = request.POST.get('notes', '')
        
        booking = Booking.objects.create(
            client=request.user,
            advocate=advocate,
            date=date,
            time=time,
            purpose=purpose,
            notes=notes
        )
        
        messages.success(request, "Consultation booked successfully!")
        return redirect('client_dashboard')
    
    return render(request, 'book_consultation.html', {
        'advocate': advocate
    })


# -------------------------
# BOOKING DETAIL
# -------------------------
@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.user not in [booking.client, booking.advocate]:
        messages.error(request, "Access denied")
        return redirect('home')
    
    documents = Document.objects.filter(booking=booking)
    
    return render(request, 'booking_detail.html', {
        'booking': booking,
        'documents': documents
    })


# -------------------------
# UPDATE BOOKING STATUS
# -------------------------
@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.user != booking.advocate:
        messages.error(request, "Only the advocate can update booking status")
        return redirect('advocate_dashboard')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        meeting_link = request.POST.get('meeting_link', '')
        
        if status in ['accepted', 'rejected', 'completed', 'cancelled']:
            booking.status = status
            if status == 'accepted' and meeting_link:
                booking.meeting_link = meeting_link
            booking.save()
            messages.success(request, f"Booking {status} successfully!")
    
    return redirect('booking_detail', booking_id=booking_id)


# -------------------------
# UPLOAD DOCUMENT
# -------------------------
@login_required
def upload_document(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.user not in [booking.client, booking.advocate]:
        messages.error(request, "Access denied")
        return redirect('home')
    
    if request.method == 'POST' and request.FILES.get('file'):
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        file = request.FILES['file']
        
        document = Document.objects.create(
            booking=booking,
            uploaded_by=request.user,
            file=file,
            title=title,
            description=description
        )
        
        messages.success(request, "Document uploaded successfully!")
        return redirect('booking_detail', booking_id=booking_id)
    
    return render(request, 'upload_document.html', {
        'booking': booking
    })


# -------------------------
# ADD REVIEW
# -------------------------
@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.user != booking.client:
        messages.error(request, "Only clients can leave reviews")
        return redirect('home')
    
    if booking.status != 'completed':
        messages.error(request, "You can only review completed consultations")
        return redirect('booking_detail', booking_id=booking_id)
    
    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this consultation")
        return redirect('booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        review = Review.objects.create(
            advocate=booking.advocate,
            client=request.user,
            booking=booking,
            rating=rating,
            comment=comment
        )
        
        # Update advocate rating
        avg_rating = Review.objects.filter(advocate=booking.advocate).aggregate(Avg('rating'))['rating__avg']
        booking.advocate.advocate_profile.rating = avg_rating or 0
        booking.advocate.advocate_profile.save()
        
        messages.success(request, "Review submitted successfully!")
        return redirect('booking_detail', booking_id=booking_id)
    
    return render(request, 'add_review.html', {
        'booking': booking
    })