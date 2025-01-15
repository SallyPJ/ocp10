from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from .models import User, Contributor, Project
from .serializers import UserSerializer, ContributorSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from common.permissions import IsAccountOwnerOrAdmin, IsProjectManagerOrAdmin, IsProjectContributorOrAdmin


class UserViewSet(ModelViewSet):
    """
        API endpoint for managing users.

        Available endpoints:
        - List all users (Admin only)
        - Retrieve a user by ID
        - Create a new user
        - Update user information
        - Partially update user information
        - Delete a user
        """
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy', 'retrieve']:
            return [IsAccountOwnerOrAdmin(), IsAuthenticated()]
        elif self.action == 'list':
            return [IsAdminUser(), IsAuthenticated()]
        return super().get_permissions()  # Default

    def get_queryset(self):
        return User.objects.all()

    @swagger_auto_schema(
        operation_summary="List all users",
        tags=["Users"],
        operation_description=(
                "Retrieve a list of all users.\n\n"
                "**Permissions required:**\n"
                "- `IsAdminUser`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="List of users retrieved successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a user",
        tags=["Users"],
        operation_description=(
                "Retrieve detailed information about a specific user by their ID.\n\n"
                "**Permissions required:**\n"
                "- `IsAccountOwnerOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="User details retrieved successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new user",
        tags=["Users"],
        operation_description=(
                "Create a new user account. This operation does not require authentication.\n\n"
                "**Security:**\n"
                "- No authentication required."
        ),
        responses={
            201: openapi.Response(description="User created successfully."),
            400: openapi.Response(description="Invalid input data."),
        }
    )
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Update a user",
        tags=["Users"],
        operation_description=(
                "Update all details of an existing user.\n\n"
                "**Permissions required:**\n"
                "- `IsAccountOwnerOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="User updated successfully."),
            400: openapi.Response(description="Invalid input data."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a user",
        tags=["Users"],
        operation_description=(
                "Update specific fields of an existing user's information.\n\n"
                "**Permissions required:**\n"
                "- `IsAccountOwnerOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(
                description="User updated successfully.",
                schema=UserSerializer()
            ),
            400: openapi.Response(
                description="Invalid input data.",
            ),
            401: openapi.Response(
                description="Unauthorized. Authentication credentials were not provided.",
            ),
            403: openapi.Response(
                description="Forbidden. You do not have permission to perform this action.",
            ),
            404: openapi.Response(
                description="Not Found. The specified user does not exist.",
            ),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a user",
        tags=["Users"],
        operation_description=(
                "Delete an existing user account.\n\n"
                "**Permissions required:**\n"
                "- `IsAccountOwnerOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            204: openapi.Response(description="User deleted successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ContributorViewSet(ModelViewSet):
    serializer_class = ContributorSerializer
    http_method_names = ['get', 'post', 'delete']
    # Default queryset to avoid issues during  Swagger schema generation
    queryset = Contributor.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'destroy']:
            return [IsAuthenticated(), IsProjectManagerOrAdmin()]
        elif self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsProjectContributorOrAdmin()]
        return super().get_permissions()  # Default

    def get_queryset(self):
        """
        Returns a queryset of contributors. For Swagger schema generation,
        it returns an empty queryset to prevent issues with AnonymousUser.
        """
        # For Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Contributor.objects.none()

        # Normal runtime behavior
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return Contributor.objects.filter(project_id=project_id)
        return Contributor.objects.all()

    @swagger_auto_schema(
        operation_summary="List contributors",
        tags=["Contributors"],
        operation_description=(
                "Retrieve a list of all contributors for a specific project.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectContributorOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="List of contributors retrieved successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a contributor",
        tags=["Contributors"],
        operation_description=(
                "Retrieve details of a specific contributor associated with a project.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectManagerOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            200: openapi.Response(description="Contributor details retrieved successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
            404: openapi.Response(description="Not Found. The specified contributor does not exist."),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add a contributor",
        tags=["Contributors"],
        operation_description=(
                "Add a new contributor to a specific project.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectManagerOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            201: openapi.Response(description="Contributor added successfully."),
            400: openapi.Response(description="Invalid input data."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
        }
    )
    def create(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_pk')
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise ValidationError("The specified project does not exist.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if Contributor.objects.filter(project=project, user=user).exists():
            raise ValidationError("This user is already a contributor to this project.")
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Remove a contributor",
        tags=["Contributors"],
        operation_description=(
                "Remove a contributor from a specific project.\n\n"
                "**Permissions required:**\n"
                "- `IsAuthenticated`\n"
                "- `IsProjectManagerOrAdmin`\n\n"
                "**Security:**\n"
                "- Bearer Token authentication is required."
        ),
        security=[{"Bearer": []}],
        responses={
            204: openapi.Response(description="Contributor removed successfully."),
            401: openapi.Response(description="Unauthorized. Authentication credentials were not provided."),
            403: openapi.Response(description="Forbidden. You do not have permission to perform this action."),
        }
    )
    def destroy(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_pk')
        contributor_id = self.kwargs.get('pk')
        try:
            contributor = Contributor.objects.get(id=contributor_id, project__id=project_id)
        except Contributor.DoesNotExist:
            return Response({"detail": "Contributor not found for this project."}, status=status.HTTP_404_NOT_FOUND)
        contributor.delete()
        return Response({"detail": "Contributor successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
