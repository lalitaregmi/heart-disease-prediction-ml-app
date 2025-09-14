from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Article, PreventionTip
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'name', 'is_staff', 'is_superuser', 'last_assessment_prediction', 'last_assessment_probability', 'last_assessment_timestamp')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        (_('Assessment Info'), {'fields': ('last_assessment_prediction', 'last_assessment_probability', 'last_assessment_timestamp')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Article)
admin.site.register(PreventionTip)
