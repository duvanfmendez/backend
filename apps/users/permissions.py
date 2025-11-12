from rest_framework.permissions import BasePermission


class IsAdministrador(BasePermission):
    """Permiso solo para administradores"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.rol == 'administrador'


class IsGestor(BasePermission):
    """Permiso solo para gestores"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.rol == 'gestor'


class IsSupervisor(BasePermission):
    """Permiso solo para supervisores"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.rol == 'supervisor'


class IsAdministradorOrGestor(BasePermission):
    """Permiso para administradores o gestores"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.rol in ['administrador', 'gestor']
        )


class IsAdministradorOrSupervisor(BasePermission):
    """Permiso para administradores o supervisores"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.rol in ['administrador', 'supervisor']
        )


class CanManagePQRS(BasePermission):
    """Permiso para gestionar PQRS (administradores y gestores)"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Administradores pueden hacer todo
        if request.user.rol == 'administrador':
            return True
        
        # Gestores solo pueden ver y responder
        if request.user.rol == 'gestor':
            # Permitir GET (ver) y POST en acciones específicas
            if request.method in ['GET', 'POST']:
                return True
            # No permitir DELETE ni editar datos básicos
            return False
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Permiso a nivel de objeto individual"""
        
        # Administradores pueden ver/editar cualquier PQRS
        if request.user.rol == 'administrador':
            return True
        
        # Gestores solo pueden ver/editar PQRS de su área
        if request.user.rol == 'gestor':
            # Si la PQRS tiene área asignada, verificar que coincida
            if obj.area_responsable:
                return obj.area_responsable == request.user.area
            # Si no tiene área, permitir (para que puedan asignarla)
            return True
        
        return False
    