from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .models import User, Contributor, Project
from user.serializers import UserSerializer, ContributorSerializer
from application.serializers import ProjectSerializer
from rest_framework.response import Response
from rest_framework import status


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer

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
