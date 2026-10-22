from rest_framework.permissions import BasePermission
from .models import User


class IsEntrepreneur(BasePermission):
    """
    Allows access only to authenticated entrepreneurs.
    """
    message = 'Доступ разрешен только предпринимателям.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_entrepreneur)


class IsBankOfficer(BasePermission):
    """
    Allows access only to authenticated bank officers (underwriters) or staff.
    """
    message = 'Доступ разрешен только сотрудникам банка (андеррайтерам).'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_bank_officer)
