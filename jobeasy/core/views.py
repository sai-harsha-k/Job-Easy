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
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from .models import UserProfile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from .models import Jobdetails
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.urls import reverse
from .utils import create_inverted_index, refine_mbti_with_baseline,prepro
import joblib
from functools import reduce
import operator


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'core/password_change_done.html'


def index(request):
    """Render and return the app's main or 'index' page."""
    return render(request, 'core/index.html')

@csrf_protect
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

@login_required
@csrf_exempt
def final_mbti_prediction(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        initial_mbti_type = data.get('initial_mbti_type')
        text_answers = data.get('text_answers')

        # Preprocess the text answers
        preprocessed_text = prepro(text_answers)

        # Initialize dictionaries to store predictions and confidences for each dimension
        predictions = {}
        confidences = {}

        # Define confidence thresholds for each dimension
        thresholds = {'I-E': 0.75, 'N-S': 0.75, 'T-F': 0.65, 'J-P': 0.65}

        # Load, predict, and obtain confidences with CatBoost for I-E, N-S, and J-P dimensions
        for dimension in ['I-E', 'N-S', 'J-P']:
            vectorizer_path = f'core/ml_models/vectorizer_{dimension}.pkl'
            model_path = f'core/ml_models/{dimension}_CatBoost.pkl'
            
            vectorizer = joblib.load(vectorizer_path)
            catboost_model = joblib.load(model_path)

            vectorized_text = vectorizer.transform([preprocessed_text])
            prediction_proba = catboost_model.predict_proba(vectorized_text)

            # Assuming the second column represents the probability of the positive class
            confidence = prediction_proba[0][1]  
            prediction = catboost_model.predict(vectorized_text)

            predictions[dimension] = prediction[0]
            confidences[dimension] = confidence

        # Load, predict, and obtain confidences with SVM for T-F dimension
        tf_vectorizer_path = 'core/ml_models/vectorizer_T-F.pkl'
        tf_model_path = 'core/ml_models/T-F_SVM.pkl'
        
        tf_vectorizer = joblib.load(tf_vectorizer_path)
        svm_model = joblib.load(tf_model_path)

        vectorized_text = tf_vectorizer.transform([preprocessed_text])
        # SVM's decision function can be used as a proxy for confidence scores
        confidence = svm_model.decision_function(vectorized_text)[0]

        tf_prediction = svm_model.predict(vectorized_text)
        predictions['T-F'] = tf_prediction[0]
        # Normalize SVM confidence to a [0,1] scale if necessary
        confidences['T-F'] = (confidence + 1) / 2  

        # Use predictions and confidences to refine the MBTI type
        final_mbti_type = refine_mbti_with_baseline(initial_mbti_type, predictions, confidences, thresholds)
        print(final_mbti_type)

        

        return JsonResponse({'final_mbti_type': final_mbti_type})

    return JsonResponse({'error': 'Invalid request'}, status=400)



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
    matching_jobs = Jobdetails.objects.filter(mbti=mbti_type)[:50]

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
        # Filter job details based on job title, company name, or location containing the query
        jobdetails = Jobdetails.objects.filter(
            Q(job_title__icontains=query) | 
            Q(company__icontains=query) | 
            Q(location__icontains=query)
        )[:10]  # Limit the number of suggestions to 10

        # Create suggestion objects containing job title, company name, location, and job ID
        suggestions = [
            {
                'id': job.job_id,
                'text': f"{job.job_title} at {job.company} - {job.location}",
                'url': reverse('core:job_details', kwargs={'job_id': job.job_id})
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
    try:
        # Fetch the current user's profile
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the user profile does not exist
        return render(request, 'core/error.html', {'message': 'User profile not found.'})

    # Extract skills from the user's profile; assuming it's stored as a JSON array
    user_skills = user_profile.skills if user_profile.skills else []

    if not user_skills:
        # If the user has no skills listed, return an empty result
        return render(request, 'core/skill_matching_jobs.html', {'jobs': []})

    # Build the Q object for filtering jobs by skills
    skills_query = Q()
    for skill in user_skills:
        skills_query |= Q(skills__icontains=skill.strip().lower())

    # Fetch matching jobs from the database, ordered by job posting date
    matching_jobs = Jobdetails.objects.filter(skills_query).order_by('-job_posting_date')[:50]

    # Paginate the results
    paginator = Paginator(matching_jobs, 10)  # Show 10 jobs per page
    page = request.GET.get('page')

    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    # Render the template with the matching jobs and pagination data
    return render(request, 'core/skill_matching_jobs.html', {'jobs': jobs})

def filtered_jobs_view(request):
    # Get the current user's profile
    user_profile = request.user.profile

    # Get the user's skills
    user_skills = user_profile.skills.split(',') if user_profile.skills else []

    # Get the user's MBTI type
    mbti_type = user_profile.mbti_type

    # Fetch jobs matching both skills and MBTI type
    matching_jobs = Jobdetails.objects.filter(
        Q(mbti=mbti_type) & 
        reduce(operator.or_, (Q(skills__icontains=skill.strip().lower()) for skill in user_skills))
    ).distinct()[:50]  # Limit to 50 jobs

    return render(request, 'core/filtered_jobs.html', {'matching_jobs': matching_jobs})