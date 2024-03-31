from django.urls import path
from . import views
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

app_name = 'core'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='core/login.html'), name='login_url'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('upload-resume/', views.handle_resume_upload, name='upload_resume'),
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz-questions/', views.quiz_questions, name='quiz_questions'),
    path('display-skills/', views.display_skills, name='display_skills'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('password_change/', PasswordChangeView.as_view(template_name='core/password_change_form.html', success_url='/core/password_change/done/'), name='change_password'),
    path('password_change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('save-mbti-profile/', views.save_mbti_to_profile, name='save_mbti_profile'),
    path('matching-jobs/<str:mbti_type>/', views.matching_jobs_view, name='matching_jobs'),
    path('autocomplete_search/', views.autocomplete_search, name='autocomplete_search'),
    path('jobs/<int:job_id>/', views.job_details, name='job_details'),
    path('search/', views.search, name='search'),
    path('search-jobs-by-skills/', views.search_jobs_by_skills, name='search_jobs_by_skills'),
    path('final-mbti-prediction/', views.final_mbti_prediction, name='final_mbti_prediction'),
]
