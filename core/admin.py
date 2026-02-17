from django.contrib import admin
from .models import Structure, Badge, User, BadgeHistory, BadgeAssignment, BadgeEndorsement

# Register your models here.
@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'referent_first_name', 'referent_last_name', 'badge_count')
    list_filter = ('type',)
    search_fields = ('name', 'description', 'referent_last_name')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'issuing_structure', 'created_at')
    list_filter = ('level', 'issuing_structure')
    search_fields = ('name', 'description')
    #filter_horizontal = ('valid_structures',)

@admin.register(User)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username','email','first_name','last_name','is_staff', 'address')
    search_fields = ('username', 'first_name', 'last_name', 'address')

@admin.register(BadgeHistory)
class BadgeHistoryAdmin(admin.ModelAdmin):
    list_display = ('badge', 'action', 'timestamp', 'details')
    list_filter = ('action', 'timestamp')
    search_fields = ('badge__name', 'action', 'details')
    date_hierarchy = 'timestamp'

@admin.register(BadgeAssignment)
class BadgeAssignmentAdmin(admin.ModelAdmin):
    list_display = ('badge', 'user', 'assigned_by', 'assigned_date')
    list_filter = ('assigned_date',)
    search_fields = ('badge__name', 'user__username', 'user__first_name', 'user__last_name')
    date_hierarchy = 'assigned_date'

@admin.register(BadgeEndorsement)
class BadgeEndorsementAdmin(admin.ModelAdmin):
    list_display = ('badge', 'structure', 'endorsed_by', 'endorsed_date')
    list_filter = ('endorsed_date',)
    search_fields = ('badge__name', 'structure__name')
    date_hierarchy = 'endorsed_date'
