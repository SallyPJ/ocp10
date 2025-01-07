from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .models import User, Contributor, Project
from user.serializers import UserSerializer, ContributorSerializer
from application.serializers import ProjectSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from common.permissions import IsAccountOwnerOrAdmin

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]  # Accessible à tout le monde
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAccountOwnerOrAdmin()]  # Réservé aux admins
        elif self.action == 'list':
            return [IsAdminUser()]  # Accessible aux utilisateurs connectés
        return super().get_permissions()  # Défaut

    def get_queryset(self):
        return User.objects.all()

    def create(self, request, *args, **kwargs):
        # Vérifiez si la requête contient une liste
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)

        # Validez et sauvegardez les données
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContributorViewSet(ModelViewSet):
    serializer_class = ContributorSerializer
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]  # Accessible à tout le monde
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAccountOwnerOrAdmin()]  # Réservé aux admins
        elif self.action == 'list':
            return [IsAdminUser()]  # Accessible aux utilisateurs connectés
        return super().get_permissions()  # Défaut


    def get_queryset(self):
        """
        Retourne soit tous les contributeurs, soit ceux liés à un projet spécifique.
        """
        project_id = self.kwargs.get('project_pk')  # Vérifie si un project_id est fourni
        if project_id:
            # Retourne uniquement les contributeurs d'un projet spécifique
            return Contributor.objects.filter(project__project_id=project_id)
        # Retourne tous les contributeurs si aucun project_id n'est spécifié
        return Contributor.objects.all()


    def perform_create(self, serializer):
        # Récupérer le project_id depuis l'URL imbriquée
        project_id = self.kwargs.get('project_pk')

        # Vérifier que le projet existe
        try:
            project = Project.objects.get(project_id=project_id)
        except Project.DoesNotExist:
            raise ValidationError("Le projet spécifié n'existe pas.")

        # Vérifier si l'utilisateur est déjà contributeur du projet
        user = serializer.validated_data['user']
        if Contributor.objects.filter(project=project, user=user).exists():
            raise ValidationError("Cet utilisateur est déjà contributeur de ce projet.")

        # Associer le projet au contributeur et sauvegarder
        serializer.save(project=project)