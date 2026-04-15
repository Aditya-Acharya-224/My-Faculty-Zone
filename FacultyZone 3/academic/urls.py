from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('library/', views.library, name='library'),
    path('upload/', views.upload_resource, name='upload'),
    path('syllabus/', views.syllabus_progress, name='syllabus'),
    path('doubts/', views.doubt_room, name='doubt_room'),
    path('timetable/', views.timetable_view, name='timetable'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('my-feedback/', views.teacher_feedback_view, name='teacher_feedback'),
    path('signup/', views.signup_view, name='signup'),
    path('doubts/answer/<int:doubt_id>/', views.answer_doubt, name='answer_doubt'),
    # Duplicate route removed: syllabus_tracker exists but we map to syllabus_progress
    path('syllabus/toggle/<int:item_id>/', views.toggle_syllabus_item, name='toggle_syllabus'),
    path('registration/', views.registration_view, name='registration_page'),
    
]
