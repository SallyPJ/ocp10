from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from .models import User, Contributor, Project
from user.serializers import UserSerializer, ContributorSerializer
from application.serializers import ProjectSerializer
from rest_framework.response import Response
from rest_framework import status
from user.permissions import IsAdminAuthenticated

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAdminAuthenticated]
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

    def get_queryset(self):
        return Contributor.objects.all()
    @action(detail=False, methods=['get'])
    def list_projects(self, request):
        # Récupérer l'utilisateur connecté
        user = request.user

        # Obtenir tous les projets où l'utilisateur est contributeur
        contributor_projects = Project.objects.filter(contributors__user=user)

        # Sérialiser les projets
        serializer = ProjectSerializer(contributor_projects, many=True)
        return Response(serializer.data)

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