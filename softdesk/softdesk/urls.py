"""
URL configuration for softdesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from user.views import UserViewSet, ContributorViewSet
from application.views import ProjectViewSet, IssueViewSet, CommentViewSet

# Main router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'projects', ProjectViewSet, basename='project')
# router.register(r'contributors', ContributorViewSet, basename='contributors')
# router.register(r'issues', IssueViewSet, basename='issues')
# router.register(r'comments', CommentViewSet, basename='comments')

# Router imbriqué pour les issues (problèmes) d'un projet
projects_router = NestedDefaultRouter(router, r'projects', lookup='project')
projects_router.register(r'issues', IssueViewSet, basename='project-issues')

# Router imbriqué pour les commentaires d'une issue
issues_router = NestedDefaultRouter(projects_router, r'issues', lookup='issue')
issues_router.register(r'comments', CommentViewSet, basename='issue-comments')

# Router imbriqué pour les contributeurs d'un projet
projects_router.register(r'contributors', ContributorViewSet, basename='project-contributors')

schema_view = get_schema_view(
    openapi.Info(
        title="SoftDesk API",
        default_version='v1',
        description="API documentation for SoftDesk projects.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="polonio.sally@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(projects_router.urls)),
    path('api/', include(issues_router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
