from rest_framework.viewsets import ModelViewSet
from .models import Project, Issue, Comment
from user.models import Contributor
from .serializers import ProjectSerializer, IssueSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from common.permissions import IsProjectManagerOrAdmin, IsProjectContributorOrAdmin, IsAuthorOrAdmin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import PermissionDenied


class ProjectViewSet(ModelViewSet):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        """
       Assign specific permissions based on the action.
       - `create`: Only authenticated users.
       - `update`, `partial_update`, `destroy`: Only authenticated users who are project managers or admins.
       - `list`: Only authenticated users who are contributors.
       """
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsProjectManagerOrAdmin()]
        elif self.action in ['retrieve', 'list']:
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        return super().get_permissions()  # Default

    @swagger_auto_schema(
        operation_summary="List projects",
        tags=["Projects"],
        operation_description=(
                "Retrieve a list of projects accessible to the authenticated user:\n"
                "- **Admins**: Can access all projects.\n"
                "- **Contributors**: Can access projects they are part of.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(
                "Success. Returns a list of projects.",
            ),
            401: openapi.Response(
                "Unauthorized. Authentication credentials were not provided.",
            ),
            403: openapi.Response(
                "Forbidden. Vous n'êtes pas associé à un projet",
            ),
        }
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Project.objects.all()
        projects = Project.objects.filter(contributors__user=self.request.user)
        if not projects.exists():
            raise PermissionDenied("Vous n'êtes pas associé à un projet.")
        return projects

    @swagger_auto_schema(
        operation_summary="Create a new project",
        tags=["Projects"],
        operation_description=(
                "Create a new project and associate the requesting user as the author.\n" 
                "The user is also added as a contributor with the role 'MANAGER'.   \n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            201: openapi.Response(
                description="Project created successfully.",
            ),
            400: openapi.Response(
                description="Invalid input data.",
            ),
            401: openapi.Response(
                description="Unauthorized. Authentication credentials were not provided.",
            ),
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Handle the creation of a project, including associating the user as the author
        and default role as manager.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call perform_create for the additional logic
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        Custom logic for saving the project and adding the creator as a manager contributor.
        """
        # Créer le projet avec l'utilisateur en tant qu'auteur
        project = serializer.save(author=self.request.user)

        # Ajouter l'auteur en tant que contributeur avec le rôle 'MANAGER'
        Contributor.objects.create(
            project=project,
            user=self.request.user,
            role='MANAGER'
        )

    @swagger_auto_schema(
        operation_summary="Retrieve a project",
        tags=["Projects"],
        operation_description=(
                "Fetch detailed information about a specific project by its ID.\n"
                "- **Admins**: Can access all projects.\n"
                "- **Contributors**: Can access projects they are part of.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(
                description="Success. Returns the project details.",
            ),
            401: openapi.Response(
                description="Unauthorized. Authentication credentials were not provided.",
            ),
            404: openapi.Response(
               description="Not Found. No Project matches the given query.",
            ),
            403: openapi.Response(
                "Forbidden. Vous n'êtes pas associé à un projet",
            ),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """Fetch a single project by ID."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a project",
        tags=["Projects"],
        operation_description=(
                "Update an existing project. \n"
                "- **Admins**: Can update any project.\n"
                "- **Project Managers (default : author)**: Can update their own projects.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectManagerOrAdmin`\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(
                description="Success. The project was successfully updated.",
            ),
            401: openapi.Response(
                description="Unauthorized. Authentication credentials were not provided.",
            ),
            403: openapi.Response(
                description="Forbidden. You do not have permission to perform this action.",
            ),
            404: openapi.Response(
                description="Not Found. No Project matches the given query.",
            ),
            400: openapi.Response(
                description="Bad Request. Invalid input data.",
            ),
        },
    )
    def update(self, request, *args, **kwargs):
        """Update an existing project."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a project",
        tags=["Projects"],
        operation_description=(
                "Update specific fields of an existing project.\n\n"
                "- **Admins**: Can update any project.\n"
                "- **Project Managers (default : author)**: Can update their own projects.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectManagerOrAdmin`\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(
                description="Success. Returns the updated project details.",
            ),
            400: openapi.Response(
                description="Invalid input data.",
            ),
            401: openapi.Response(
                description="Unauthorized. Authentication credentials were not provided.",
            ),
            403: openapi.Response(
                description="Forbidden. You do not have permission to update this project.",
            ),
            404: openapi.Response(
                description="Not Found. The specified project does not exist.",
            ),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Handle partial updates to a project.
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a project",
        tags=["Projects"],
        operation_description=(
                "Delete a project if the user is an admin or the project manager (default : author).\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectManagerOrAdmin`\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),

        security=[{"Bearer": []}],
        responses={
            204: openapi.Response(
                description="No Content. The project was successfully deleted.",
            ),
            401: openapi.Response(
                description="Unauthorized. Authentication credentials were not provided.",
            ),
            403: openapi.Response(
                description="Forbidden. You do not have permission to delete this project.",
            ),
            404: openapi.Response(
                description="Not Found. No Project matches the given query.",
            ),
        },
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete a project.
        """
        return super().destroy(request, *args, **kwargs)


class IssueViewSet(ModelViewSet):
    """
    ViewSet for managing issues.
    Provides CRUD operations for issues with specific permissions.
    """
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def get_permissions(self):
        """
       Assign specific permissions based on the action:
       - `create`: Only authenticated users who are contributors.
       - `update`, `partial_update`, `destroy`: Only authenticated users who are authors or admins.
       - `list`: Only authenticated users who are contributors.
       """
        if self.action == 'create':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrAdmin()]
        elif self.action in ['retrieve', 'list']:
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List issues",
        tags=["Issues"],
        operation_description=(
                "Retrieve a list of issues for projects where the authenticated user is a contributor.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="List of issues retrieved successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to view these issues."),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve an issue",
        tags=["Issues"],
        operation_description=(
                "Retrieve details of a specific issue by its ID.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="Issue details retrieved successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to view this issue."),
            404: openapi.Response(description="Not Found. The issue does not exist."),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create an issue",
        tags=["Issues"],
        operation_description=(
                "Create a new issue for a project. Only contributors can create issues.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            201: openapi.Response(description="Issue created successfully."),
            400: openapi.Response(description="Bad Request. Invalid input data."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to create this issue."),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an issue",
        tags=["Issues"],
        operation_description=(
                "Update an existing issue. Only the issue author or admins can update it.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsAuthorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="Issue updated successfully."),
            400: openapi.Response(description="Bad Request. Invalid input data."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to update this issue."),
            404: openapi.Response(description="Not Found. The issue does not exist."),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update an issue",
        tags=["Issues"],
        operation_description=(
                "Partially update specific fields of an existing issue. "
                "Only the issue author or admins can perform this action.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsAuthorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(
                description="Issue updated successfully.",
            ),
            400: openapi.Response(
                description="Bad Request. Invalid input data.",
            ),
            401: openapi.Response(
                description="Unauthorized. Authentication credentials were not provided.",
            ),
            403: openapi.Response(
                description="Forbidden. You do not have permission to update this issue.",
            ),
            404: openapi.Response(
                description="Not Found. The issue does not exist.",
            ),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete an issue",
        tags=["Issues"],
        operation_description=(
                "Delete an issue. Only the issue author or admins can delete it.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsAuthorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            204: openapi.Response(description="Issue deleted successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to delete this issue."),
            404: openapi.Response(description="Not Found. The issue does not exist."),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrAdmin()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List all comments of an issue",
        tags=["Comments"],
        operation_description=(
                "Retrieve a list of comments linked to an issue. Only contributors "
                "to the project can access the comments.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="Success. Returns a list of comments."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
        },
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Retrieve a comment",
        tags=["Comments"],
        operation_description=(
                "Retrieve a specific comment by its ID. Only contributors to the project can access the comment.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="Success. Returns the comment details."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
            404: openapi.Response(description="Not Found. The comment does not exist."),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a comment",
        tags=["Comments"],
        operation_description=(
                "Create a new comment. The comment have to be linked to an issue. "
                "Only contributors to the project can create comments.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            201: openapi.Response(description="Comment created successfully."),
            400: openapi.Response(description="Bad Request. Invalid input data."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Update a comment",
        tags=["Comments"],
        operation_description=(
                "Update an existing comment. Only the author of the comment or admins can perform this action.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsAuthorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="Comment updated successfully."),
            400: openapi.Response(description="Bad Request. Invalid input data."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
            404: openapi.Response(description="Not Found. The comment does not exist."),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a comment",
        tags=["Comments"],
        operation_description=(
                "Partially update specific fields of an existing comment. "
                "Only the author or admins can perform this action.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsAuthorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="Comment partially updated successfully."),
            400: openapi.Response(description="Bad Request. Invalid input data."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
            404: openapi.Response(description="Not Found. The comment does not exist."),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a comment",
        tags=["Comments"],
        operation_description=(
                "Delete an existing comment. Only the author or admins can delete a comment.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsAuthorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            204: openapi.Response(description="Comment deleted successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
            404: openapi.Response(description="Not Found. The comment does not exist."),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
