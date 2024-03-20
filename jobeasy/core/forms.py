from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'phone_number']

class ResumeUploadForm(forms.Form):
    resume = forms.FileField(label='Upload your resume')

