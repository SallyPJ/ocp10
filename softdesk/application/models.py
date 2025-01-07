from django.db import models
import uuid


class Project(models.Model):

    PROJECT_TYPE_CHOICES = [
        ('backend', 'Back-end'),
        ('frontend', 'Front-end'),
        ('ios', 'iOS'),
        ('android', 'Android'),
    ]
    project_id = models. UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    project_name = models.CharField(max_length=100, null=False)
    project_description = models.CharField(max_length=400, null=True, blank=True)
    project_type = models.CharField(max_length=10, choices=PROJECT_TYPE_CHOICES)
    project_author = models.ForeignKey('user.User', on_delete=models.CASCADE, null=False)
    project_created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name

    class Meta:
        ordering = ['project_created_time']

class Issue(models.Model):

    ISSUE_PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    ISSUE_TAG_CHOICES = [
        ('bug', 'Bug'),
        ('task', 'Task'),
        ('feature', 'Feature'),
    ]

    ISSUE_STATUS_CHOICES = [
        ('to_do', 'To do'),
        ('in_progress', 'In progress'),
        ('done', 'Done'),
    ]

    issue_name = models.CharField(max_length=100, null=False)
    issue_description = models.CharField(max_length=400, null=True, blank=True)
    issue_priority = models.CharField(max_length=10, choices=ISSUE_PRIORITY_CHOICES)
    issue_tag = models.CharField(max_length=10, choices=ISSUE_TAG_CHOICES)
    issue_status = models.CharField(max_length=11, choices=ISSUE_STATUS_CHOICES)
    issue_author = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='issues_author', null=False)
    project = models.ForeignKey('application.Project', on_delete=models.CASCADE, related_name='issues', null=False)
    issue_assignee = models.ForeignKey('user.Contributor', on_delete=models.CASCADE,
                                       related_name='assigned_issues')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.issue_name


class Comment(models.Model):
    comment_description = models.CharField(max_length=400, null=False)
    author = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='comments', null=False)
    issue = models.ForeignKey('Issue', on_delete=models.CASCADE, related_name='comments', null=False)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment
