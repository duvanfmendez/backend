from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Modelo de usuario personalizado con roles para el sistema PQRS"""
    
    ROLE_CHOICES = [
        ('administrador', 'Administrador'),
        ('gestor', 'Gestor'),
        ('supervisor', 'Supervisor'),
    ]
    
    rol = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='gestor',
        verbose_name='Rol'
    )
    area = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name='Área'
    )
    telefono = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name='Teléfono'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"