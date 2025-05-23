from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import timedelta, datetime

class Lecture(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    qr_code = models.CharField(max_length=255, unique=True, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def generate_qr_code(self):
        self.qr_code = str(uuid.uuid4())  # Generate a unique QR code
        self.expires_at = datetime.now() + timedelta(minutes=10)  # Expires in 10 mins
        self.save()

    def __str__(self):
        return self.title

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lecture') 

from django.contrib.auth import authenticate, login

"""def student_login(request):
    if request.method == "POST":
        username = request.POST["username"]  
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect after login
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'attendance/login.html')"""
