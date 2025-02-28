from django.shortcuts import render, redirect
from django.urls import resolve
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


@login_required(login_url="login")
def user_profile(request):
    """
    Render the user profile page.

    This view requires the user to be authenticated. If the user is not logged in,
    they are redirected to the login page.

    **Context:**
    - `profile_page`: A boolean flag indicating that the profile page is active.

    **Template:**
    - `api/profile.html`
    """
    context = {
        "profile_page": True
    }
    return render(request, "api/profile.html", context)


def user_login(request):
    """
    Handle user authentication and login.

    If the user is already authenticated, they are redirected to the profile page.
    If login credentials are valid, the user is authenticated and redirected to
    the requested next page (if provided) or the profile page.

    **Request Method:** POST
    - `email`: User's email address (used as the username).
    - `password`: User's password.
    - `next`: Optional, URL to redirect the user after login.

    **Context:**
    - `navbar`: A boolean indicating whether to show the navbar.
    - `left`: A boolean indicating whether to show the left sidebar.
    - `next`: The next URL parameter, used for redirection after login.

    **Template:**
    - `api/login.html`

    **Redirects:**
    - If already authenticated: Redirect to `profile`.
    - If login succeeds: Redirect to `next` URL or `profile`.
    - If login fails: Redirect to `login` with an error message.
    """
    if request.user.is_authenticated:
        messages.warning(request, _("Avval tizimdan chiqishingiz talab etiladi"))
        return redirect("profile")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        next_page_url = request.POST.get("next")

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            if next_page_url:
                try:
                    url = resolve(next_page_url).url_name
                except:
                    url = "profile"  # Default fallback if the next_page_url is invalid
            else:
                url = "profile"

            messages.success(request, _("Xush kelibsiz") + user.full_name + "👋")
            return redirect(url)

        # Incorrect username or password
        # TODO: Does not show error message yet in the frontend
        messages.error(request, _("Username yoki Parol xato"))
        return redirect("login")

    context = {
        "navbar": False,
        "left": False,
        "next": request.GET.get("next")
    }
    return render(request, "api/login.html", context)


def user_logout(request):
    """
    Log out the authenticated user and redirect to the login page.

    **Redirects:**
    - Redirects to `login` after logout.
    """
    logout(request)
    return redirect("login")
