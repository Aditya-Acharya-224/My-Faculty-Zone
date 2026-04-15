from django.db import models
from django.contrib.auth.models import User

# 1. NOTICES (Visible to Everyone)
class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# 2. DIGITAL LIBRARY (Teachers upload, Students view)
class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('BOOK', 'Reference Book'),
        ('PYQ', 'Previous Year Question'),
        ('NOTE', 'Lecture Notes'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to='resources/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.category})"

# 3. DOUBT ROOM (Students ask, Teachers answer)
class Doubt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asked_doubts')
    subject = models.CharField(max_length=100)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    answered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'is_staff': True}, related_name='answered_doubts')
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject}: {self.question[:30]}"

# 4. SYLLABUS TRACKING (Teacher updates progress)
# Subject model is defined later with the correct schema matching migrations

# 5. FEEDBACK SYSTEM (Student rates Teacher)
class Feedback(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True}, related_name='received_feedback')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedback')
    comment = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.teacher.username}"

# 6. TEACHER TIMETABLE (Blank Editable Grid for Teachers)
class TeacherTimetable(models.Model):
    teacher = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    data = models.JSONField(default=dict) # Stores the grid: {"Monday-1": "5A", ...}

    def __str__(self):
        return f"Timetable for {self.teacher.username}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})

    def get_progress(self):
        total = self.items.count()
        if total == 0: return 0
        completed = self.items.filter(is_completed=True).count()
        return int((completed / total) * 100)

class SyllabusItem(models.Model):
    # 'related_name' MUST be 'items' for our template loop to work
    order = models.PositiveIntegerField(default=0)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='items')
    topic_name = models.CharField(max_length=255)
    is_subtopic = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.topic_name

