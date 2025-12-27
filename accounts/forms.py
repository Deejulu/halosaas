from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email address')
    phone_number = forms.CharField(max_length=15, required=False, label='Phone (optional)')
    # Only allow 'restaurant_owner' and 'customer' roles for registration
    NON_ADMIN_ROLES = [role for role in CustomUser.ROLE_CHOICES if role[0] != 'admin']
    role = forms.ChoiceField(choices=NON_ADMIN_ROLES, label='I am a')
    
    # Security Questions
    security_question1 = forms.ChoiceField(
        choices=CustomUser.SECURITY_QUESTIONS, 
        required=True, 
        label='Security Question 1'
    )
    security_answer1 = forms.CharField(
        max_length=100, 
        required=True, 
        label='Answer to Question 1',
        widget=forms.TextInput(attrs={'placeholder': 'Your answer'})
    )
    
    security_question2 = forms.ChoiceField(
        choices=CustomUser.SECURITY_QUESTIONS, 
        required=True, 
        label='Security Question 2'
    )
    security_answer2 = forms.CharField(
        max_length=100, 
        required=True, 
        label='Answer to Question 2',
        widget=forms.TextInput(attrs={'placeholder': 'Your answer'})
    )
    
    security_question3 = forms.ChoiceField(
        choices=CustomUser.SECURITY_QUESTIONS, 
        required=True, 
        label='Security Question 3'
    )
    security_answer3 = forms.CharField(
        max_length=100, 
        required=True, 
        label='Answer to Question 3',
        widget=forms.TextInput(attrs={'placeholder': 'Your answer'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose another.')
        return username

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'role', 'password1', 'password2', 
                 'security_question1', 'security_answer1', 'security_question2', 'security_answer2', 
                 'security_question3', 'security_answer3')
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
        user.security_question1 = self.cleaned_data.get('security_question1')
        user.security_answer1 = self.cleaned_data.get('security_answer1').lower().strip()
        user.security_question2 = self.cleaned_data.get('security_question2')
        user.security_answer2 = self.cleaned_data.get('security_answer2').lower().strip()
        user.security_question3 = self.cleaned_data.get('security_question3')
        user.security_answer3 = self.cleaned_data.get('security_answer3').lower().strip()
        if commit:
            user.save()
        return user


class AccountRecoveryForm(forms.Form):
    email = forms.EmailField(required=True, label='Email Address')
    
    security_question1 = forms.CharField(max_length=200, required=True, label='Security Question 1')
    security_answer1 = forms.CharField(max_length=100, required=True, label='Your Answer')
    
    security_question2 = forms.CharField(max_length=200, required=True, label='Security Question 2') 
    security_answer2 = forms.CharField(max_length=100, required=True, label='Your Answer')
    
    security_question3 = forms.CharField(max_length=200, required=True, label='Security Question 3')
    security_answer3 = forms.CharField(max_length=100, required=True, label='Your Answer')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email address'})
        self.fields['security_answer1'].widget.attrs.update({'placeholder': 'Your answer'})
        self.fields['security_answer2'].widget.attrs.update({'placeholder': 'Your answer'})
        self.fields['security_answer3'].widget.attrs.update({'placeholder': 'Your answer'})
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        
        if email:
            try:
                user = CustomUser.objects.get(email__iexact=email)
                # Populate the questions from the user's saved questions
                if user.security_question1:
                    self.fields['security_question1'].initial = dict(CustomUser.SECURITY_QUESTIONS)[user.security_question1]
                    cleaned_data['user'] = user
                else:
                    raise forms.ValidationError('This account does not have security questions set up.')
            except CustomUser.DoesNotExist:
                raise forms.ValidationError('No account found with this email address.')
        
        return cleaned_data
    
    def clean_security_answer1(self):
        answer = self.cleaned_data.get('security_answer1', '').lower().strip()
        user = getattr(self, 'cleaned_data', {}).get('user')
        if user and user.security_answer1 and answer != user.security_answer1:
            raise forms.ValidationError('Incorrect answer to security question 1.')
        return answer
    
    def clean_security_answer2(self):
        answer = self.cleaned_data.get('security_answer2', '').lower().strip()
        user = getattr(self, 'cleaned_data', {}).get('user')
        if user and user.security_answer2 and answer != user.security_answer2:
            raise forms.ValidationError('Incorrect answer to security question 2.')
        return answer
    
    def clean_security_answer3(self):
        answer = self.cleaned_data.get('security_answer3', '').lower().strip()
        user = getattr(self, 'cleaned_data', {}).get('user')
        if user and user.security_answer3 and answer != user.security_answer3:
            raise forms.ValidationError('Incorrect answer to security question 3.')
        return answer