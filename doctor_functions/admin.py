from django.contrib import admin
from .models import UserProfileModel

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user','name', 'speciality', 'picture', 'details', 'experience', 'twitter', 'facebook', 'instagram' ]

admin.site.register(UserProfileModel, UserProfileAdmin)