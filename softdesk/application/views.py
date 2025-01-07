from rest_framework.viewsets import ModelViewSet
from .models import Project, Issue, Comment
from user.models import Contributor
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response




class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

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

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


