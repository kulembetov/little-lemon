from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import Group

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='manager').exists()

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='delivery crew').exists()

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and not (
            request.user.is_superuser or
            request.user.groups.filter(name__in=['manager', 'delivery crew']).exists()
        ) 