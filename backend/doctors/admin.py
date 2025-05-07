from django.contrib import admin
from .models import Doctor, Schedule

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'speciality')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'speciality')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('doctor', 'date', 'is_available')
