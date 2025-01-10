from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsAccountOwnerOrAdmin(BasePermission):
    """
    Permission permettant à l'admin ou à l'utilisateur connecté de modifier/supprimer son propre compte.
    """
    def has_object_permission(self, request, view, obj):
        # L'utilisateur est autorisé s'il est admin ou s'il agit sur son propre compte
        return request.user.is_superuser or obj == request.user


class IsProjectManagerOrAdmin(BasePermission):
    """
    Permission permettant uniquement aux managers d'un projet ou aux administrateurs d'ajouter des contributeurs.
    """

    def has_object_permission(self, request, view, obj):
        # Vérifier si l'utilisateur est un administrateur
        if request.user.is_superuser:
            return True

        # Vérifier si l'utilisateur a le statut "manager" dans le projet
        return obj.contributors.filter(user=request.user, role='manager').exists()


class IsProjectContributorOrAdmin(BasePermission):
    """
    Permission permettant uniquement aux contributeurs ou à l'admin d'accéder au projet.
    """

    def has_object_permission(self, request, view, obj):
        # Vérifie si l'utilisateur est admin
        if request.user.is_superuser:
            return True
        # Vérifie si l'utilisateur est contributeur du projet
        return obj.contributors.filter(user=request.user).exists()

class IsAuthorOrAdmin(BasePermission):
    """
    Permission permettant uniquement à l'auteur ou à l'administrateur
    de modifier ou supprimer une ressource.
    """
    def has_object_permission(self, request, view, obj):
        # Vérifie si l'utilisateur est admin
        if request.user.is_superuser:
            return True
        # Vérifier si l'utilisateur est l'auteur de l'issue
        if obj.author == request.user:
            # Vérifier si l'auteur est également un contributeur au projet
            if obj.project.contributors.filter(user=request.user).exists():
                return True
            else:
                raise PermissionDenied("The issue author must also be a contributor to the associated project.")

