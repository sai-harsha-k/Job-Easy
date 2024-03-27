from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import ResumeUploadForm
from django.contrib.auth.decorators import login_required
from .skillmatcher import analyze_resume_text  
import json
from .forms import UserProfileForm
from django.http import JsonResponse
from django.conf import settings
import os
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import UserProfile
from .text_Extraction import process_uploaded_resume
from .models import UserProfile
from django.contrib.auth.views import PasswordChangeDoneView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Jobdetails

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'core/password_change_done.html'


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

@login_required
def dashboard(request):
    mbti_type = None
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        mbti_type = user_profile.mbti_type
    except UserProfile.DoesNotExist:
        pass  # Handle case where user profile does not exist, if necessary

    return render(request, 'core/dashboard.html', {'mbti_type': mbti_type})

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

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard')
    else:
        form = UserProfileForm(instance=request.user.profile)

    return render(request, 'core/update_profile.html', {'form': form})

@csrf_exempt
def save_mbti_to_profile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mbti_type = data.get('mbti_type')
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.mbti_type = mbti_type
        user_profile.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

def matching_jobs_view(request, mbti_type):
    # Fetch jobs matching the MBTI type
    matching_jobs = Jobdetails.objects.filter(mbti=mbti_type)

    # Set up pagination
    paginator = Paginator(matching_jobs, 10)  # Show 10 jobs per page

    # Get the page number from the request
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the template with the paginated jobs
    return render(request, 'core/matching_jobs.html', {'page_obj': page_obj, 'mbti_type': mbti_type})