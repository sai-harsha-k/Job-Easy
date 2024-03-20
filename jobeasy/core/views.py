from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import ResumeUploadForm
from django.contrib.auth.decorators import login_required
from .skillmatcher import analyze_resume_text  
import json
from django.http import JsonResponse
from django.conf import settings
import os
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import UserProfile
from .text_Extraction import process_uploaded_resume
from .models import UserProfile

def index(request):
    """Render and return the app's main or 'index' page."""
    return render(request, 'core/index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a UserProfile object for the new user
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('core:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def display_skills(request):
    user_profile = request.user.profile  # Assuming the OneToOne relation name is 'userprofile'
    resume_text = user_profile.resume_text

    if resume_text:
        # Analyze the resume text and extract skills
        skills = analyze_resume_text(resume_text)
        return render(request, 'core/skill_results.html', {'skills': skills})
    else:
        # Handle case where no resume text is available
        return render(request, 'core/no_resume_uploaded.html')


def dashboard(request):
    return render(request, 'core/dashboard.html')

def quiz(request):
    return render(request, 'core/quiz.html')

def quiz_questions(request):
    file_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'quiz-questions.json')
    with open(file_path, 'r') as file:
        questions = json.load(file)
    return JsonResponse(questions, safe=False)


def handle_resume_upload(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        file = request.FILES['resume']
        file_type = file.content_type  # Get the content type of the uploaded file

        # Extract text from the uploaded resume file
        resume_text = process_uploaded_resume(file, file_type)  # Pass the file_type argument here

        # Update or create the user profile with the extracted resume text
        UserProfile.objects.update_or_create(
            user=request.user, 
            defaults={'resume_text': resume_text}
        )
        return redirect('core:dashboard')
    return redirect('core:dashboard')
