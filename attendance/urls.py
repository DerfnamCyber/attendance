from django.urls import path
from .views import check_location, qr_attendance_page, mark_attendance, attendance_report, download_report
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('check-location/', check_location, name='check_location'),
    path('scan-qr/', qr_attendance_page, name='qr_attendance_page'),
    path('mark-attendance/', mark_attendance, name='mark_attendance'),
    path('attendance-report/', attendance_report, name='attendance_report'),
    path('download-report/', download_report, name='download_report'),
    #path('download-report/<int=lecture_id>/', download_report, name='download_report'),
]


