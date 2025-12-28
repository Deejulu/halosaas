from django import forms
from .models import AdminFeedback

class AdminFeedbackForm(forms.ModelForm):
    class Meta:
        model = AdminFeedback
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your feedback...', 'rows': 5}),
        }
