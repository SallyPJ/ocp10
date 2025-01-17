from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from user.models import Contributor
from application.models import Project


class IsAccountOwnerOrAdmin(BasePermission):
    """
    Permission allowing only the admin or the authenticated user to modify/delete their own account.
    """
    def has_object_permission(self, request, view, obj):
        print(f"Request user: {request.user}, Object: {obj}")  # Debug log
        # L'utilisateur est autorisé s'il est admin ou s'il agit sur son propre compte
        return request.user.is_staff or obj == request.user


class IsProjectManagerOrAdmin(BasePermission):
    """
    Permission allowing only project managers or administrators to add contributors.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks permissions based on the object's ID:
        - If the object is a Project, verify the user's role as manager for the project.
        - If the object is not a Project, retrieve and verify the project ID from `project_pk` or `id` in the URL.
        """

        if request.user.is_staff:
            return True
        obj_id = obj.id
        # Check if the user is a manager of the project
        if Contributor.objects.filter(
                project=obj_id,
                user=request.user,
                role='MANAGER'
        ).exists():
            return True

        if view.action == 'create':
            project_pk = view.kwargs.get('project_pk')
            if not project_pk:
                return False
            return Contributor.objects.filter(
                project_id=project_pk,
                user=request.user,
                role='MANAGER'
            ).exists()

        project_pk = view.kwargs.get('project_pk')
        if not project_pk:
            raise PermissionDenied("Le projet n'a pas été spécifié dans l'URL.")

        try:
            # Check if the user is a contributor to the project
            is_contributor = Contributor.objects.filter(
                project=project_pk,
                user=request.user,
                role="MANAGER"
            ).exists()
            if is_contributor:
                return True
        except ValueError:
            raise PermissionDenied("Le paramètre project_pk est invalide ou mal formé.")

            # Deny access if the user is neither an admin nor a contributor
        raise PermissionDenied("Vous devez être administrateur ou contributeur pour accéder à cet élément.")


class IsProjectContributorOrAdmin(BasePermission):
    """
     Permission allowing only contributors or administrators to access the project.
    """

    def has_permission(self, request, view):
        # Administrators always have access
        if request.user.is_staff:
            return True

        # Retrieve project_pk from kwargs
        project_pk = view.kwargs.get('project_pk')
        if not project_pk:
            raise PermissionDenied("Le projet n'a pas été spécifié dans l'URL.")

        try:
            # Check if the user is a contributor to the project
            is_contributor = Contributor.objects.filter(
                project=project_pk,
                user=request.user
            ).exists()
            if is_contributor:
                return True
        except ValueError:
            raise PermissionDenied("Le paramètre project_pk est invalide ou mal formé.")

        # Deny access if the user is neither an admin nor a contributor
        raise PermissionDenied("Vous devez être administrateur ou contributeur pour accéder à cet élément.")


class IsAuthorOrAdmin(BasePermission):
    """
    Permission allowing only the author or an administrator to modify or delete a resource.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is an admin
        if request.user.is_staff:
            return True
        # Check if the user is the author of the issue
        if obj.author == request.user:
            # Check if the author is also a contributor to the project
            if obj.project.contributors.filter(user=request.user).exists():
                return True
            else:
                raise PermissionDenied("The issue author must also be a contributor to the associated project.")
