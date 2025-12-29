from django import forms
from .models import CustomUser

class SecurityQuestionLoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    answer1 = forms.CharField(label='Answer to Security Question 1', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Answer 1'}))
    answer2 = forms.CharField(label='Answer to Security Question 2', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Answer 2'}))
    answer3 = forms.CharField(label='Answer to Security Question 3', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Answer 3'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        answer1 = cleaned_data.get('answer1', '').lower().strip()
        answer2 = cleaned_data.get('answer2', '').lower().strip()
        answer3 = cleaned_data.get('answer3', '').lower().strip()
        try:
            user = CustomUser.objects.get(username__iexact=username)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError('No user found with this username.')
        if (user.security_answer1.lower().strip() != answer1 or
            user.security_answer2.lower().strip() != answer2 or
            user.security_answer3.lower().strip() != answer3):
            raise forms.ValidationError('One or more answers are incorrect.')
        cleaned_data['user'] = user
        return cleaned_data
