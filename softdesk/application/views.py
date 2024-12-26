from rest_framework.viewsets import ModelViewSet
from .models import Project, Issue, Comment
from user.models import Contributor
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer




class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


