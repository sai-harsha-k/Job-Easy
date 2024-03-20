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
    path('password_change/', PasswordChangeView.as_view(template_name='core/password_change_form.html'), name='change_password'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='core/password_change_done.html'), name='password_change_done'),

]
