from rest_framework.viewsets import ModelViewSet
from .models import Project, Issue, Comment
from user.models import Contributor
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from common.permissions import IsProjectManagerOrAdmin, IsProjectContributorOrAdmin, IsAuthorOrAdmin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ProjectViewSet(ModelViewSet):
    """
    ViewSet for managing projects.
    Provides CRUD operations for projects and handles specific permissions for each operation.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        """
       Assign specific permissions based on the action.
       - `create`: Only authenticated users.
       - `update`, `partial_update`, `destroy`: Only authenticated users who are project managers or admins.
       - `list`: Only authenticated users who are contributors.
       """
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsProjectManagerOrAdmin()]
        elif self.action == 'list':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        return super().get_permissions()  # Default

    def get_queryset(self):
        """
        Retrieve projects based on user role:
        - Admin users: Access all projects.
        - Regular users: Access only projects where they are contributors.
        """
        if self.request.user.is_superuser:
            return Project.objects.all()
        return Project.objects.filter(contributors__user=self.request.user)

    @swagger_auto_schema(operation_description="Create a new project with the requesting user as the author and default role as manager.")
    def perform_create(self, serializer):
        # create a project et do association with author
        project = serializer.save(author=self.request.user)

        # Add the author as a contributor ( role = manager)
        Contributor.objects.create(
            project=project,
            user=self.request.user,
            role='MANAGER'
        )

    @swagger_auto_schema(operation_description="Update an existing project if the user is an admin or project author.")
    def update(self, request, *args, **kwargs):
        # Récupérer l'instance du projet
        instance = self.get_object()

        # Vérifier si l'utilisateur est l'auteur ou un administrateur
        if not request.user.is_superuser and instance.project_author != request.user:
            return Response(
                {"error": "Vous n'avez pas la permission de modifier ce projet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Appeler la méthode parente pour gérer la mise à jour
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Delete a project if the user is an admin or project author.")
    def destroy(self, request, *args, **kwargs):
        # Récupérer l'instance du projet
        instance = self.get_object()

        # Vérifier si l'utilisateur est administrateur ou l'auteur du projet
        if not request.user.is_superuser and instance.project_author != request.user:
            return Response(
                {"error": "Vous n'avez pas la permission de supprimer ce projet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Appeler la méthode parente pour effectuer la suppression
        return super().destroy(request, *args, **kwargs)


class IssueViewSet(ModelViewSet):
    """
    ViewSet for managing issues.
    Provides CRUD operations for issues with specific permissions.
    """
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def get_permissions(self):
        """
       Assign specific permissions based on the action:
       - `create`: Only authenticated users who are contributors.
       - `update`, `partial_update`, `destroy`: Only authenticated users who are authors or admins.
       - `list`: Only authenticated users who are contributors.
       """
        if self.action == 'create':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrAdmin()]
        elif self.action == 'list':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filter issues visible only for projects where the user is a contributor.
        """
        return Issue.objects.filter(project__contributors__user=self.request.user)

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrAdmin()]
        elif self.action == 'list':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        return super().get_permissions()


