from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, AccountRecoveryForm, SecurityQuestionsForm
from .models import CustomUser

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            
            # If customer has a preferred restaurant, redirect there
            if user.role == 'customer' and user.preferred_restaurant:
                messages.info(request, f'Taking you to {user.preferred_restaurant.name}!')
                return redirect('restaurant_detail', slug=user.preferred_restaurant.slug)
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def account_recovery(request):
    if request.method == 'POST':
        form = AccountRecoveryForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            # Show recovery information
            context = {
                'form': form,
                'recovered': True,
                'username': user.username,
                'email': user.email,
                'role': user.get_role_display(),
            }
            messages.success(request, 'Account information recovered successfully!')
            return render(request, 'accounts/account_recovery.html', context)
    else:
        form = AccountRecoveryForm()
    
    return render(request, 'accounts/account_recovery.html', {'form': form})


@login_required
def security_questions(request):
    if request.method == 'POST':
        form = SecurityQuestionsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Security questions updated successfully!')
            return redirect('dashboard')
    else:
        form = SecurityQuestionsForm(instance=request.user)
    
    return render(request, 'accounts/security_questions.html', {'form': form})