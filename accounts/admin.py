from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import *

# Register your models here.
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ['email', 'name','sapid', 'grad_year','is_staff','is_active','is_superuser']
    list_filter = ['email','name','sapid', 'grad_year','is_staff','is_active','is_superuser']

    fieldsets = (
        (None, {'fields': ('sapid', 'password')}),
        ('Personal info', {'fields': ('name', 'email')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide,'),
            'fields': ('email', 'password1', 'password2', 'name','is_staff','is_active','sapid', 'grad_year'),
        }),
    )
    search_fields = ('sapid',)
    ordering = ('sapid',)
    filter_horizontal = ()

class InterviewerAdmin(admin.ModelAdmin):
    model = Interviewer
    list_display = ['user', 'role']
    list_filter = ['user', 'role']

    fieldsets = [
        (None, {'fields': ('user', 'role', 'username')})
    ]

    search_fields = ['role']
    ordering = ['user']
    filter_horizontal = ()


class IntervieweeAdmin(admin.ModelAdmin):
    model = Interviewee
    list_display = ['user']
    list_filter = ['user']

    fieldsets = [
        (None, {'fields': ('user',)})
    ]

    # search_fields = ['role']
    ordering = ['user']
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(Interviewer, InterviewerAdmin)
admin.site.register(Interviewee, IntervieweeAdmin)
admin.site.register(Stack)
admin.site.register(Task)
admin.site.register(Questionnaire)
admin.site.register(Interview)