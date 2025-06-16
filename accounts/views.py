from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.conf import settings
from .forms import LoginForm, RegisterForm, ProfileForm

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
                return redirect(next_url)
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect(settings.LOGOUT_REDIRECT_URL)

@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Smart Device Manager.')
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})