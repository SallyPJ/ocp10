from rest_framework import serializers
from .models import Project, Issue, Comment
from user.models import Contributor


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'type', 'created_time']


class ProjectDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author','author_username',
                  'created_time']
        read_only_fields = ['author', 'created_time', 'author_username']


class IssueListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Issue
        fields = ['id', 'name', 'priority', 'status', 'author_username', 'author_username', 'created_time']
        read_only_fields = ['author', 'author_username']


class IssueDetailSerializer(serializers.ModelSerializer):
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
        Retrieve and validate the project based on project_pk in the URL.
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
        Validate that the assignee is a contributor to the project.
        """
        project = self._get_project()

        # Check if the assignee is a contributor
        if not Contributor.objects.filter(user=value.user, project=project).exists():
            raise serializers.ValidationError("The assignee must be a contributor of the specified project.")
        return value

    def create(self, validated_data):
        """
        Automatically add the project and author when creating an issue.
        """
        project = self._get_project()   # Use utility method to get the project

        # Automatically assign the project and author
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
        """
        Automatically add the authenticated user as the author of the comment.
        """
        user = self.context['request'].user
        issue_pk = self.context['view'].kwargs.get('issue_pk')

        # Check if the user is a contributor to the project's issue
        try:
            issue = Issue.objects.get(pk=issue_pk)
            is_contributor = Contributor.objects.filter(user=user, project=issue.project).exists()
            if not (is_contributor or user.is_staff):
                raise serializers.ValidationError("The author must be a contributor of the project's issue.")
        except Issue.DoesNotExist:
            raise serializers.ValidationError("The issue does not exist.")

        # Add the author and issue to the validated data
        validated_data['author'] = user
        validated_data['issue'] = issue
        return super().create(validated_data)
