from rest_framework import serializers
from .models import Project, Issue, Comment
from user.models import Contributor


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author',
                  'created_time']
        read_only_fields = ['author', 'created_time']


class IssueSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    assignee_username = serializers.CharField(source='assignee.user.username', read_only=True)
    class Meta:
        model = Issue
        fields = ['id', 'name', 'description', 'priority', 'tag', 'status', 'author',
                  'author_username', 'project', 'assignee', 'assignee_username',
                  'created_time']
        read_only_fields = ['author', 'author_username', 'assignee_username', 'created_time', 'project']
    def _get_project(self):
        """
        Récupère et valide le projet à partir du project_pk dans l'URL.
        """
        project_pk = self.context['view'].kwargs.get('project_pk')
        if not project_pk:
            raise serializers.ValidationError("Project ID is required.")
        try:
            return Project.objects.get(id=project_pk)
        except Project.DoesNotExist:
            raise serializers.ValidationError("The specified project does not exist.")

    def validate_assignee(self, value):
        """
        Valide que l'assignee est un contributeur du projet.
        """
        project = self._get_project()  # Utilise la méthode utilitaire pour obtenir le projet

        # Vérifie si l'assignee est un contributeur
        if not Contributor.objects.filter(user=value.user, project=project).exists():
            raise serializers.ValidationError("The assignee must be a contributor of the specified project.")
        return value

    def create(self, validated_data):
        """
        Ajoute automatiquement le projet et l'auteur lors de la création d'une issue.
        """
        project = self._get_project()  # Utilise la méthode utilitaire pour obtenir le projet

        # Assigner automatiquement le projet et l'auteur
        validated_data['project'] = project
        validated_data['author'] = self.context['request'].user

        return super().create(validated_data)



class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'description', 'author', 'author_username', 'issue', 'created_time']
        read_only_fields = ['author', 'author_username', 'created_time', 'issue']

    def create(self, validated_data):
        # Ajouter automatiquement l'utilisateur connecté comme auteur
        user = self.context['request'].user
        issue_pk = self.context['view'].kwargs.get('issue_pk')

        # Vérifier que l'utilisateur est un contributeur du projet de l'issue
        try:
            issue = Issue.objects.get(pk=issue_pk)
            is_contributor = Contributor.objects.filter(user=user, project=issue.project).exists()
            if not is_contributor:
                raise serializers.ValidationError("The author must be a contributor of the project's issue.")
        except Issue.DoesNotExist:
            raise serializers.ValidationError("The issue does not exist.")

        # Ajouter l'auteur et l'issue dans les données validées
        validated_data['author'] = user
        validated_data['issue'] = issue
        return super().create(validated_data)
