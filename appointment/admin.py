from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppoinmentAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'name', 'email', 'phone', 'date', 'time','status']
    date_hierarchy = ('date')
    list_filter = ['date', 'doctor', ]
    list_per_page = 20
    search_fields = ['doctor', 'name', ]
