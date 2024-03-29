from django import forms
from .models import UserProfile,Jobdetails
from django_select2.forms import Select2Widget

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'phone_number']

class ResumeUploadForm(forms.Form):
    resume = forms.FileField(label='Upload your resume')

class JobAutocompleteForm(forms.ModelForm):
    class Meta:
        model = Jobdetails
        fields = ['job_title']

    job_title = forms.ModelChoiceField(
        queryset=Jobdetails.objects.all(),
        widget=Select2Widget
    )