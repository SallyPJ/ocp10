from django.db import models
import uuid


class Project(models.Model):

    PROJECT_TYPE_CHOICES = [
        ('BACKEND', 'Back-end'),
        ('FRONTEND', 'Front-end'),
        ('IOS', 'iOS'),
        ('ANDROID', 'Android'),
    ]

    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=400, null=True, blank=True)
    type = models.CharField(max_length=10, choices=PROJECT_TYPE_CHOICES)
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, null=False)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_time']


class Issue(models.Model):

    ISSUE_PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    ISSUE_TAG_CHOICES = [
        ('BUG', 'Bug'),
        ('TASK', 'Task'),
        ('FEATURE', 'Feature'),
    ]

    ISSUE_STATUS_CHOICES = [
        ('TO_DO', 'To do'),
        ('IN_PROGRESS', 'In progress'),
        ('DONE', 'Done'),
    ]

    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=400, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=ISSUE_PRIORITY_CHOICES)
    tag = models.CharField(max_length=10, choices=ISSUE_TAG_CHOICES)
    status = models.CharField(max_length=11, choices=ISSUE_STATUS_CHOICES, default='TO_DO')
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='issues_author', null=False)
    project = models.ForeignKey('application.Project', on_delete=models.CASCADE, related_name='issues', null=False)
    assignee = models.ForeignKey('user.Contributor', on_delete=models.CASCADE,
                                 related_name='assignee_issues')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    description = models.CharField(max_length=400, null=False)
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='comments', null=False)
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, related_name='comments', null=False)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description
