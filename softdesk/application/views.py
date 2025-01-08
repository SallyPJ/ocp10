from rest_framework.viewsets import ModelViewSet
from .models import Project, Issue, Comment
from user.models import Contributor
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from common.permissions import IsProjectManagerOrAdmin, IsProjectContributorOrAdmin, IsAuthorOrAdmin


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]  # Accessible à tout le monde
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsProjectManagerOrAdmin()]  # Réservé aux admins
        elif self.action == 'list':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]  # Accessible aux utilisateurs connectés
        return super().get_permissions()  # Défaut

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Project.objects.all()
        return Project.objects.filter(contributors__user=self.request.user)

    def perform_create(self, serializer):
        # Crée le projet et l'associe à l'auteur
        project = serializer.save(project_author=self.request.user)

        # Ajoute l'auteur en tant que contributeur
        Contributor.objects.create(
            project=project,
            user=self.request.user,
            role='MANAGER'
        )
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
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrAdmin()]
        elif self.action == 'list':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        # Filtrer les issues visibles uniquement pour les projets auxquels l'utilisateur est contributeur
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


