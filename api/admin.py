#from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import UserProfile, Plant, Disease, Logbook, Reminder, Admin


# ==========================================
# USER PROFILE ADMIN
# ==========================================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'phone_no',
        'is_first_time_user',
        'created_at'
    ]
    list_filter = ['is_first_time_user', 'skipped_intro']
    search_fields = ['user__username', 'phone_no']
    readonly_fields = ['created_at', 'updated_at']


# ==========================================
# PLANT ADMIN
# ==========================================
@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = [
        'common_name',
        'scientific_name',
        'hindi_name',
        'plant_type',
        'size',
        'toxicity',
        'edibility',
        'is_common'
    ]
    list_filter = [
        'plant_type',
        'size',
        'toxicity',
        'edibility',
        'is_common'
    ]
    search_fields = [
        'common_name',
        'scientific_name',
        'hindi_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'common_name',
                'scientific_name',
                'hindi_name',
                'plant_type',
                'size'
            )
        }),
        ('Safety Information', {
            'fields': ('toxicity', 'edibility')
        }),
        ('Care Instructions', {
            'fields': (
                'watering',
                'sunlight',
                'soil_type',
                'temperature',
                'care_tips'
            )
        }),
        ('Additional Info', {
            'fields': ('fun_facts', 'image_url', 'is_common')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ==========================================
# DISEASE ADMIN
# ==========================================
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'plant',
        'severity',
        'created_at'
    ]
    list_filter = ['severity', 'plant']
    search_fields = ['name', 'symptoms', 'treatment']
    readonly_fields = ['created_at', 'updated_at']


# ==========================================
# LOGBOOK ADMIN
# ==========================================
@admin.register(Logbook)
class LogbookAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'plant',
        'date',
        'is_favorite',
        'location'
    ]
    list_filter = ['is_favorite', 'date']
    search_fields = [
        'user__username',
        'plant__common_name',
        'notes',
        'location'
    ]
    readonly_fields = ['date', 'created_at', 'updated_at']
    date_hierarchy = 'date'


# ==========================================
# REMINDER ADMIN
# ==========================================
@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'plant',
        'reminder_type',
        'frequency',
        'next_reminder_date',
        'is_active'
    ]
    list_filter = ['reminder_type', 'frequency', 'is_active']
    search_fields = ['user__username', 'plant__common_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'next_reminder_date'


# ==========================================
# ADMIN MODEL ADMIN
# ==========================================
@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'get_email',
        'role',
        'is_active',
        'created_at'
    ]
    list_filter = ['role', 'is_active']
    search_fields = [
        'name',
        'user__email',
        'user__username'
    ]
    readonly_fields = ['created_at', 'updated_at']

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'