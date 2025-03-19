from django.urls import path
from .views import check_location, qr_attendance_page, mark_attendance, proceed, attendance_report, download_report, generate_qr_code, login, dashboard, logout, register
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('proceed/', proceed, name='proceed'),
    path('generate-qr-code/<int:lecture_id>/', generate_qr_code, name='generate_qr_code'),
    path('check-location/', check_location, name='check_location'),
    path('scan-qr/', qr_attendance_page, name='qr_attendance_page'),
    path('mark-attendance/', mark_attendance, name='mark_attendance'),
    path('attendance-report/', attendance_report, name='attendance_report'),
    #   path('download-report/', download_report, name='download_report'),
    path('download-report/<int:lecture_id>/', download_report, name='download_report'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    
]


