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

admin.site.register(User, UserAdmin)
admin.site.register(Interviewer)
admin.site.register(Interviewee)
admin.site.register(Stack)
admin.site.register(Task)
admin.site.register(Score)
admin.site.register(Interview)
admin.site.register(Application)
admin.site.register(ApplicationStack)
admin.site.register(Panel)
admin.site.register(Question)