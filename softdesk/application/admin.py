from django.contrib import admin
from .models import Project, Issue, Comment
from user.models import Contributor


# ContributorInline - Gestion des contributeurs liés à un projet
class ContributorInline(admin.TabularInline):
    """
    Inline view for managing contributors within the Project admin page.
    - Enables adding contributors directly when managing a project.
    """
    model = Contributor
    extra = 1  # Number of empty forms displayed by default


# ProjectAdmin - Gestion des projets
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for managing projects.
    - Displays key fields such as name, author, and created_time.
    - Includes contributors inline for better visibility.
    """
    list_display = ('name', 'author', 'type', 'created_time')  # Columns in the admin list view
    list_filter = ('type', 'created_time')  # Filters by project type and creation date
    search_fields = ('name', 'description', 'author__username')  # Enables search by these fields
    ordering = ('-created_time',)  # Orders projects by creation date, newest first

    # Inline contributors management
    inlines = [ContributorInline]


# CommentInline - Gestion des commentaires liés à un ticket
class CommentInline(admin.TabularInline):
    """
    Inline view for managing comments within the Issue admin page.
    - Enables adding comments directly when managing an issue.
    """
    model = Comment
    extra = 1  # Number of empty forms displayed by default


# IssueAdmin - Gestion des tickets
@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """
    Admin interface for managing issues (tickets).
    - Displays ticket name, status, priority, author, and project.
    - Provides filters for status, priority, and associated project.
    """
    list_display = ('name', 'status', 'priority', 'author', 'project')  # Columns in the admin list view
    list_filter = ('status', 'priority', 'project')  # Filters by these fields
    search_fields = ('name', 'description', 'author__username', 'project__name')  # Searchable fields
    ordering = ('-created_time',)  # Orders issues by creation date, newest first

    # Inline comments management
    inlines = [CommentInline]


# ContributorAdmin - Gestion directe des contributeurs
@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    """
    Admin interface for managing contributors.
    - Displays contributors, their associated project, and their role.
    - Provides filters for role and project.
    """
    list_display = ('user', 'project', 'role')  # Columns in the admin list view
    list_filter = ('role', 'project')  # Filters by role and project
    search_fields = ('user__username', 'project__name')  # Searchable fields
    ordering = ('project', 'user')  # Orders contributors by project and user


# CommentAdmin - Gestion directe des commentaires
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing comments.
    - Displays comment description, author, and associated issue.
    - Provides filters for issues, authors, and creation date.
    """
    list_display = ('description', 'author', 'issue', 'created_time')  # Columns in the admin list view
    list_filter = ('issue', 'author', 'created_time')  # Filters by issue, author, and creation date
    search_fields = ('description', 'author__username', 'issue__name')  # Searchable fields
    ordering = ('-created_time',)  # Orders comments by creation date, newest first
