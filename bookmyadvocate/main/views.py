from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User


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

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="client",
        )
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

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="advocate",
            is_active_advocate=True
        )
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

            if user.role == "client":
                return redirect("client_dashboard")
            elif user.role == "advocate":
                return redirect("advocate_dashboard")

        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


# -------------------------
# LOGOUT
# -------------------------
def user_logout(request):
    logout(request)
    return redirect("login")


# -------------------------
# DASHBOARDS
# -------------------------
@login_required
def client_dashboard(request):
    return render(request, "client_dashboard.html")


@login_required
def advocate_dashboard(request):
    return render(request, "advocate_dashboard.html")
