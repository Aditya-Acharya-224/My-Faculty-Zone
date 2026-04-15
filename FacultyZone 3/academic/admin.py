from django.contrib import admin
from .models import Subject, SyllabusItem

# 1. First, remove any lines like admin.site.register(Subject) if they exist at the bottom

class SyllabusItemInline(admin.TabularInline):
    model = SyllabusItem
    extra = 1

# 2. Use the decorator ONLY ONCE
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher')
    inlines = [SyllabusItemInline]

# 3. Register SyllabusItem separately if you want to edit items individually
@admin.register(SyllabusItem)
class SyllabusItemAdmin(admin.ModelAdmin):
    list_display = ('topic_name', 'subject', 'is_subtopic', 'is_completed')
    list_filter = ('subject', 'is_completed')

