from django.contrib import admin
from .models import Lecture, Attendance

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'qr_code', 'expires_at')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lecture', 'timestamp')
    list_filter = ('lecture',)