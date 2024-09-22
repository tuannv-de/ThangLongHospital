from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import Slider, Doctor
from django.views.generic import ListView, DetailView, TemplateView
from doctor_functions.models import UserProfileModel


class HomeView(ListView):
    template_name = 'hospital/index.html'
    queryset = Slider.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['sliders'] = Slider.objects.all()
        context['experts'] = UserProfileModel.objects.all()
        return context


class DoctorListView(ListView):
    template_name = 'hospital/team.html'
    queryset = UserProfileModel.objects.all()
    paginate_by = 8


class DoctorDetailView(DetailView):
    template_name = 'hospital/team-details.html'
    queryset = UserProfileModel.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctors"] = UserProfileModel.objects.all()
        return context


