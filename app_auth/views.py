from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user:
            return HttpResponse("Login successful")

        messages.error(request, _("Username yoki Parol xato"))
        return redirect("login")

    context = {}
    return render(request, "app_auth/login.html", context)
