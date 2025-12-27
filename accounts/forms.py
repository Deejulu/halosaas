from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email address')
    phone_number = forms.CharField(max_length=15, required=False, label='Phone (optional)')
    # Only allow 'restaurant_owner' and 'customer' roles for registration
    NON_ADMIN_ROLES = [role for role in CustomUser.ROLE_CHOICES if role[0] != 'admin']
    role = forms.ChoiceField(choices=NON_ADMIN_ROLES, label='I am a')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')
        return username

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'role', 'password1', 'password2')
        help_texts = {
            'username': 'Choose a short username. You can change it later.',
            'role': 'Pick the option that best describes your account.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Improve form usability and accessibility with placeholders and ARIA
        self.fields['username'].widget.attrs.update({
            'placeholder': 'e.g. alex123',
            'autofocus': 'autofocus',
            'aria-label': 'username',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'you@example.com',
            'type': 'email',
            'aria-label': 'email address',
        })
        self.fields['phone_number'].widget.attrs.update({
            'placeholder': '+1234567890',
            'aria-label': 'phone number',
        })
        self.fields['role'].widget.attrs.update({
            'aria-label': 'account role',
        })
        # Password fields (inherited from UserCreationForm)
        if 'password1' in self.fields:
            self.fields['password1'].help_text = (
                'Use at least 8 characters; avoid common words or sequences.'
            )
            self.fields['password1'].widget.attrs.update({
                'placeholder': 'Create a strong password',
                'aria-label': 'password',
            })
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'placeholder': 'Repeat your password',
                'aria-label': 'confirm password',
            })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.role = self.cleaned_data.get('role')
        user.phone_number = self.cleaned_data.get('phone_number', '')
        if commit:
            user.save()
        return user