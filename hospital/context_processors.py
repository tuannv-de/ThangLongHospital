from .models import Doctor
from doctor_functions.models import UserProfileModel

def footer_content(request):
    doctors = UserProfileModel.objects.all()
    context = {
        'doctors': doctors
    }
    return context
