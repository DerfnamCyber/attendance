from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  # ✅ Import the form
from geopy.distance import geodesic
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Lecture, Attendance
import openpyxl
import json
from .models import Lecture
import qrcode
import io
import base64
from io import BytesIO

# Replace with actual lecture hall coordinates
LECTURE_HALL_LOCATION = (6.671640973230205, -1.5628947760371927)

def home(request):
    return render(request, 'home.html')
    
def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return render(request, 'gps_verification.html')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def proceed(request):
    return render(request, 'gps_verification.html')

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        if password1 != password2:
            return render(request, 'register.html', {"error_message" : "Passwords do not match."})
        
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error_message": "Username is already taken."})
        user = User.objects.create_user(username=username, password=password1)
        user.save()
        #form = UserCreationForm(request.POST)
        #if form.is_valid():
        #    user = form.save()
        #    auth_login(request, user)
        auth_login(request, user)
        return redirect('login') #After successful registration
        #form = UserCreationForm()
    return render(request, 'register.html')

def logout(request):
    auth_logout(request)  # ✅ Logs out the user
    return redirect('login')  # ✅ Redirects to login page


@login_required
def dashboard(request):
    lectures = Lecture.objects.all()
    return render(request, 'dashboard.html', {'lectures': lectures})

def generate_qr_code(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    lecture.generate_qr_code()
    qr = qrcode.make(f"Lecture {lecture_id}")
    #qr = qrcode.make(lecture.qr_code)
    #buffer = io.BytesIO()
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_data = base64.b64encode(buffer.getvalue()).decode()
    return HttpResponse(buffer.getvalue(), content_type='image/png')
    #return JsonResponse({"qr-code": f"data:image/png;base64, {qr_data}"})


@login_required
def check_location(request):
    if request.method == "GET":
        user_lat = float(request.GET.get('lat', 0))
        user_lng = float(request.GET.get('lng', 0))
        
        user_location = (user_lat, user_lng)
        distance = geodesic(LECTURE_HALL_LOCATION, user_location).meters
        if distance <= 5:
            request.session['location_verified'] = True  # Store in session
            #return render(request, 'scan_qr.html')
            return JsonResponse({'status': 'allowed', 'distance': round(distance, 2)})
        else:
            return JsonResponse({'status': 'denied', 'distance': round(distance, 2)})
    

@login_required
def qr_attendance_page(request):
    if not request.session.get('location_verified', False):
        return redirect('gps_verification_page')  # Force GPS check first
    return render(request, 'scan_qr.html')

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


@login_required
def attendance_report(request):
    if not request.user.is_staff:  # Only lecturers can access
        return render(request, 'error.html', {'message': 'Access Denied'})

    lectures = Lecture.objects.all()
    selected_lecture = request.GET.get('lecture')
    attendance_records = Attendance.objects.filter(lecture_id=selected_lecture) if selected_lecture else None

    return render(request, 'attendance_report.html', {
        'lectures': lectures,
        'attendance_records': attendance_records
    }) 




def download_report(request, lecture_id):
    lecture = Lecture.objects.get(id=lecture_id)
    attendance_records = Attendance.objects.filter(lecture=lecture)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Attendance Report"

    # Headers
    sheet.append(["Student Name", "Index Number", "Timestamp"])

    # Attendance Data
    for record in attendance_records:
        sheet.append([record.student.get_full_name(), record.student.username, record.timestamp])

    # Response as Excel file
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="Attendance_{lecture.title}.xlsx"'
    workbook.save(response)

    return response 

     
