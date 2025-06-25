from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .forms import LoginForm, RegisterForm, ProfileForm, UserUpdateForm

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('appliance_list')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'appliance_list')
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
    return redirect('accounts:login')

@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect('appliance_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)  # define here!

        if form.is_valid():
            user = form.save()
            profile = user.profile  # created by signal

            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()

            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Smart Device Manager.')
            return redirect('appliance_list')
    else:
        form = RegisterForm()
        profile_form = ProfileForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'profile_form': profile_form,
    })
@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'form': user_form,
        'profile_form': profile_form,
    })