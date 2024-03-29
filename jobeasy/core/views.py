from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from .models import Jobdetails
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.urls import reverse
from .utils import create_inverted_index

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
        skills_data  = analyze_resume_text(resume_text)
        skill_names = [skill[0] for skill in skills_data]
        # Join skill names into a comma-separated string
        user_profile.skills = ','.join(skill_names)
        user_profile.save()
        return render(request, 'core/skill_results.html', {'skills': skills_data})
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

def job_details(request, job_id):
    job = get_object_or_404(Jobdetails, pk=job_id)
    return render(request, 'core/job_details.html', {'job': job})

def autocomplete_search(request):
    query = request.GET.get('q', '')
    suggestions = []
    if query:
        jobdetails = Jobdetails.objects.filter(job_title__icontains=query)[:10]  # Limit the results
        suggestions = [
            {
                'id': job.job_id,
                'text': job.job_title,
                'url': reverse('core:job_details', kwargs={'job_id': job.job_id})  # Generate URL for job details
            }
            for job in jobdetails
        ]
    return JsonResponse({'suggestions': suggestions})

def search(request):
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)  # Get the page number from the request

    if query:
        # Fuzzy search results
        fuzzy_results = Jobdetails.objects.filter(
            Q(job_title__icontains=query) |  # Fuzzy match on job title
            Q(company__icontains=query)      # Fuzzy match on company name
        )

        # Full-text search results
        fulltext_results = Jobdetails.objects.annotate(
            match=RawSQL("MATCH(job_title, company) AGAINST (%s IN BOOLEAN MODE)", (query,))
        ).filter(match__gt=0)

        # Combine results, ensuring uniqueness by using set (to avoid duplicate results)
        combined_results = set(list(fuzzy_results) + list(fulltext_results))

        # Paginator setup
        paginator = Paginator(list(combined_results), 10)  # Show 10 results per page
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            results = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver the last page of results.
            results = paginator.page(paginator.num_pages)

    else:
        results = []

    return render(request, 'core/search_results.html', {'results': results, 'query': query})

@login_required
def search_jobs_by_skills(request):
    # Fetch the current user's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Extract skills from the user's profile; it's stored as JSON
    user_skills = user_profile.skills if user_profile.skills else []

    # Fetch all jobs from the database
    all_jobs = Jobdetails.objects.all()

    # Create the inverted index
    inverted_index = create_inverted_index(all_jobs)

    # Use 'inverted_index' to quickly find jobs by skills
    matching_job_ids = set()
    for skill in user_skills:
        skill = skill.lower()  # Assuming skills are stored in lowercase in the inverted index
        if skill in inverted_index:
            matching_job_ids.update(inverted_index[skill])

    # Fetch matching jobs from the database
    matching_jobs = Jobdetails.objects.filter(job_id__in=matching_job_ids)

    # Render some template with the matching jobs
    return render(request, 'core/skill_matching_jobs.html', {'jobs': matching_jobs})