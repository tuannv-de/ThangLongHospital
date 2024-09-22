from django.db import models
from django.utils import timezone
from doctor_functions.models import UserProfileModel

class Appointment(models.Model):
    time_choices = (
        ('morning', "Morning"),
        ('evening', "Evening")
    )
    
    status_choices = (
        ('pending', 'Đang chờ'),
        ('accepted', 'Chấp nhận'),
        ('completed', 'Đã khám')
    )

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    doctor = models.ForeignKey(
        UserProfileModel, on_delete=models.CASCADE, related_name='appointments'
    )
    date = models.DateField(default=timezone.now)
    time = models.CharField(choices=time_choices, max_length=10)
    note = models.TextField(blank=True, null=True)

    # Thêm trường trạng thái
    status = models.CharField(
        max_length=10,
        choices=status_choices,
        default='pending'  # Giá trị mặc định là 'Đang chờ'
    )

    def __str__(self):
        return f"{self.name} - {self.doctor.name} - {self.get_status_display()}"
