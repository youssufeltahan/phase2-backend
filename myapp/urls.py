from django.urls import path, re_path
from . import views

urlpatterns = [
    path('sign_up_view/', views.signUp, name='sign_up_view'),
    path('sign_in/', views.sign_in, name='signin'),
    path('insert_slot/', views.addSlot, name='insert_slot'),
    path('select_doctor/', views.getDoctorName, name='select_doctor'),
    path('show_slots/<str:docslots>', views.get_available_slots, name='show_slots'),
    path('choose_slot/', views.choose_slot, name='choose_slot'),
    path('update_appointment/', views.update_appointment, name='update_appointment'),
    re_path(r'^cancel_appointment/$', views.cancel_appointment, name='cancel'),
    path('patient_slots/', views.get_patient_slots, name='patient_schedule'),


]

