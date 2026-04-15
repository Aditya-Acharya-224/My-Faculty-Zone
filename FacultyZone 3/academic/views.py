from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notice, Resource, Doubt, Subject, Feedback, TeacherTimetable, SyllabusItem
from django.contrib.auth.forms import UserCreationForm  # For Signup
from django.contrib.auth import login
from django.contrib.auth.models import User

# 1. LANDING PAGE (Choice for Student or Teacher)
def landing(request):
    return render(request, 'dashboard.html')

# 2. SEPARATE INTERFACES (Logic for Role-Based Access)
@login_required
def dashboard(request):
    notices = Notice.objects.all().order_by('-date_posted')
    if request.user.is_staff:
        # Teacher Interface
        return render(request, 'teacher_dashboard.html', {'notices': notices})
    else:
        # Student Interface
        return render(request, 'student_dashboard.html', {'notices': notices})

# 3. STUDENT MODULES
@login_required
def library(request):
    books = Resource.objects.filter(category='BOOK')
    pyqs = Resource.objects.filter(category='PYQ')
    notes = Resource.objects.filter(category='NOTE')
    return render(request, 'library.html', {'books': books, 'pyqs': pyqs, 'notes': notes})

@login_required
def library_view(request):
    # Fetch all resources uploaded to the database
    resources = Resource.objects.all().order_by('-uploaded_at')
    
    # Categorize them so the frontend can display them in sections
    # Use the choice keys defined in Resource.CATEGORY_CHOICES
    notes = resources.filter(category='NOTE')
    books = resources.filter(category='BOOK')
    pyqs = resources.filter(category='PYQ')

    return render(request, 'library.html', {
        'notes': notes,
        'books': books,
        'pyqs': pyqs,
        'all_resources': resources
    })


@login_required
def doubt_room(request):
    if request.method == 'POST' and not request.user.is_staff:
        subject = request.POST.get('subject')
        question = request.POST.get('question')
        # Ensure student is linked to the logged-in user
        Doubt.objects.create(student=request.user, subject=subject, question=question)
        return redirect('doubt_room')
    
    # Get all doubts to display
    doubts = Doubt.objects.all().order_by('-created_at')
    return render(request, 'doubt_room.html', {'doubts': doubts})

# 4. TEACHER MODULES
@login_required
def upload_resource(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Use .get() but ensure the names match your HTML exactly
        title = request.POST.get('title')
        category = request.POST.get('category')
        file = request.FILES.get('file') # Files MUST come from request.FILES

        # Add a simple check to prevent saving if data is missing
        if title and file:
            Resource.objects.create(
                title=title, 
                category=category, 
                file=file, 
                uploaded_by=request.user
            )
            return redirect('library')
        else:
            # You can add an error message here later
            pass

    return render(request, 'upload.html')


@login_required
def timetable_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    timetable_obj, _ = TeacherTimetable.objects.get_or_create(teacher=request.user)
    if request.method == 'POST':
        cell_id = request.POST.get('cell_id')
        content = request.POST.get('content')
        data = timetable_obj.data
        data[cell_id] = content
        timetable_obj.data = data
        timetable_obj.save()
        return JsonResponse({'status': 'success'})
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    periods = range(1, 9)
    full_grid = []
    for day in days:
        row = {'day_name': day, 'cells': []}
        for p in periods:
            key = f"{day}-{p}"
            row['cells'].append({'id': key, 'content': timetable_obj.data.get(key, "")})
        full_grid.append(row)
    return render(request, 'timetable.html', {'full_grid': full_grid, 'periods': periods})

# 5. SHARED PROGRESS TRACKING
@login_required
def syllabus_progress(request):
    # 1. HANDLE POST (Adding Topic)
    if request.method == 'POST' and request.user.is_staff:
        subj_id = request.POST.get('subject_id')
        name = request.POST.get('topic_name')
        is_sub = request.POST.get('is_subtopic') == 'on'
        
        if subj_id and name:
            target_subject = Subject.objects.get(id=subj_id)
            SyllabusItem.objects.create(
                subject=target_subject, 
                topic_name=name, 
                is_subtopic=is_sub
            )
            # This returns a response after POST
            return redirect('syllabus')

    # 2. HANDLE GET (Fetching Data)
    if request.user.is_staff:
        subjects = Subject.objects.filter(teacher=request.user)
    else:
        subjects = Subject.objects.all()

    # 3. FINAL RETURN (This was likely missing or indented wrongly)
    # This MUST be at the bottom level of the function
    return render(request, 'syllabus.html', {'subjects': subjects})

@login_required
def submit_feedback(request):
    teachers = User.objects.filter(is_staff=True)
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher')
        teacher_user = User.objects.get(id=teacher_id)
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')
        Feedback.objects.create(
            teacher=teacher_user, 
            student=request.user, 
            comment=comment, 
            rating=rating
        )
        return redirect('dashboard')
    return render(request, 'feedback_form.html', {'teachers': teachers})

@login_required
def teacher_feedback_view(request):
    # Only staff (Teachers) should access this page
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Filter feedback where the teacher is the logged-in user
    feedbacks = Feedback.objects.filter(teacher=request.user).order_by('-submitted_at')
    
    return render(request, 'teacher_feedback.html', {'feedbacks': feedbacks})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after signup
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def answer_doubt(request, doubt_id):
    # Only Teachers can answer
    if not request.user.is_staff:
        return redirect('dashboard')

    doubt = Doubt.objects.get(id=doubt_id)
    
    if request.method == 'POST':
        answer_text = request.POST.get('answer')
        doubt.answer = answer_text
        doubt.answered_by = request.user
        doubt.is_resolved = True
        doubt.save()
        return redirect('doubt_room')
    
    return render(request, 'answer_doubt.html', {'doubt': doubt})

@login_required
def syllabus_tracker(request):
    # 1. Handle Toggle (The AJAX part)
    if 'toggle' in request.path:
        # (This part stays the same as previous)
        pass 

    # 2. Handle Add Topic (Teacher Only)
    if request.method == 'POST' and request.user.is_staff:
        subj_id = request.POST.get('subject_id')
        name = request.POST.get('topic_name')
        is_sub = 'is_subtopic' in request.POST
        if subj_id and name:
            SyllabusItem.objects.create(
                subject_id=subj_id, 
                topic_name=name, 
                is_subtopic=is_sub
            )
        return redirect('syllabus')

    # 3. GET DATA: Ensure subjects exist
    if request.user.is_staff:
        subjects = Subject.objects.filter(teacher=request.user)
    else:
        subjects = Subject.objects.all()

    return render(request, 'syllabus.html', {'subjects': subjects})

def registration_view(request):
    return render(request, 'registration/Registration.html')


@login_required
def toggle_syllabus_item(request, item_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        item = SyllabusItem.objects.get(id=item_id)
        item.is_completed = not item.is_completed # Toggles True/False
        item.save()
        
        # Calculate new progress for the progress bar
        new_progress = item.subject.get_progress()
        
        return JsonResponse({
            'status': 'success',
            'is_completed': item.is_completed,
            'new_progress': new_progress
        })
    except SyllabusItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)