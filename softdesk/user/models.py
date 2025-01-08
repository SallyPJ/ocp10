from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from application.models import Project


class User(AbstractUser):
    username = models.CharField(
        "username",
        max_length=150,
        unique=True,
        null=False,
        blank=False,
    )
    age = models.PositiveIntegerField(
        null=False,
        default=18,
        validators=[MinValueValidator(15, "L'utilisateur doit avoir au moins 15 ans.")])
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)


class Contributor(models.Model):
    ROLE_CHOICES = [
        ('MANAGER', 'Project Manager'),
        ('CONTRIBUTOR', 'Contributor'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributors')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CONTRIBUTOR')

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.username} - {self.project.name}"

