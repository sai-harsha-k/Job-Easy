# admin.py
from django.contrib import admin
from .models import Jobdetails
from .forms import JobAutocompleteForm

@admin.register(Jobdetails)
class JobdetailsAdmin(admin.ModelAdmin):
    form = JobAutocompleteForm
    list_display = ['job_title', 'company', 'job_posting_date']  # Specify fields to display in the list view
    search_fields = ['job_title', 'company', 'job_description', 'responsibilities', 'skills']  # Define searchable fields
    fields = ['job_title', 'company', 'job_description', 'responsibilities', 'skills', 'job_posting_date', 'location', 'country', 'work_type', 'salary_range', 'job_portal', 'mbti']  # Specify fields to display in detail view
