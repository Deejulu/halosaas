from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, AccountRecoveryForm, SecurityQuestionsForm
from .models import CustomUser
from .security_question_login_form import SecurityQuestionLoginForm

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
    password_login_failed = False
    user = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            request.session['show_welcome_overlay'] = True
            request.session['show_loader_after_login'] = True
            if user.role == 'customer' and hasattr(user, 'preferred_restaurant') and user.preferred_restaurant:
                messages.info(request, f'Taking you to {user.preferred_restaurant.name}!')
                return redirect('restaurant_detail', slug=user.preferred_restaurant.slug)
            return redirect('dashboard')
        else:
            password_login_failed = True
    return render(request, 'accounts/login.html', {
        'password_login_failed': password_login_failed,
    })


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

def security_question_login(request):
    form = SecurityQuestionLoginForm(request.POST or None)
    login_failed = False
    if request.method == 'POST':
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}! (Security Questions)')
            request.session['show_welcome_overlay'] = True
            request.session['show_loader_after_login'] = True
            return redirect('dashboard')
        else:
            login_failed = True
    return render(request, 'accounts/security_question_login.html', {
        'form': form,
        'login_failed': login_failed,
    })