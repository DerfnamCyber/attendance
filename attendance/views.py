from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from geopy.distance import geodesic
import json
from .models import Lecture
import qrcode
import io
import base64

# Replace with actual lecture hall coordinates
LECTURE_HALL_LOCATION = (37.7749, -122.4194)

def home(request):
    return render(request, 'gps_verification.html')

def generate_qr_code(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    lecture.generate_qr_code()

    qr = qrcode.make(lecture.qr_code)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_data = base64.b64encode(buffer.getvalue()).decode()

    return JsonResponse({"qr_code": qr_data, "expires_at": lecture.expires_at.strftime('%Y-%m-%d %H:%M:%S')})


@login_required
def check_location(request):
    if request.method == "GET":
        user_lat = float(request.GET.get('lat', 0))
        user_lng = float(request.GET.get('lng', 0))
        
        user_location = (user_lat, user_lng)
        distance = geodesic(LECTURE_HALL_LOCATION, user_location).meters

        if distance <= 50:
            request.session['location_verified'] = True  # Store in session
            return JsonResponse({'status': 'allowed', 'distance': round(distance, 2)})
        else:
            return JsonResponse({'status': 'denied', 'distance': round(distance, 2)})

@login_required
def qr_attendance_page(request):
    if not request.session.get('location_verified', False):
        return redirect('gps_verification_page')  # Force GPS check first
    return render(request, 'attendance/scan_qr.html')

@login_required
def mark_attendance(request):
    if request.method == "POST":
        data = json.loads(request.body)
        student = request.user  # Assuming authentication is by index number
        qr_code_data = data.get("qr_code")

        lecture = Lecture.objects.filter(qr_code=qr_code, expires_at_gte=now()).first()

        if lecture:
            # Prevent duplicate attendance
            if Attendance.objects.filter(student=student, lecture=lecture).exists():
                return JsonResponse({'status': 'error', 'message': 'You have already marked attendance!'})
            
            # Record attendance
            Attendance.objects.create(student=student, lecture=lecture)
            return JsonResponse({'status': 'success', 'message': 'Attendance marked successfully!'})

        return JsonResponse({'status': 'error', 'message': 'Invalid or expired QR Code!'})

        
