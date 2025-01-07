from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from application.models import Project



# Create your models here.

class User(AbstractUser):
    age = models.PositiveIntegerField(null=False, default=18)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.username :
            raise ValidationError('L\'utilisateur doit avoir un nom d\'utilisateur.')
        if self.age and self.age < 15:
            raise ValidationError('L\'utilisateur doit avoir au moins 15 ans.')
        super().save(*args, **kwargs)


class Contributor(models.Model):
    contributor_id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributors')

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.username} - {self.project.project_name}"

