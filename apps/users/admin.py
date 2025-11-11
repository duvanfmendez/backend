from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuración del admin para el modelo User personalizado"""
    
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'rol',
        'area',
        'is_staff',
        'is_active',
    ]
    
    list_filter = [
        'rol',
        'area',
        'is_staff',
        'is_active',
    ]
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'area', 'telefono')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'area', 'telefono')
        }),
    )