from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin interface for the User model.
    - Displays additional fields like 'age', 'can_be_contacted', and 'can_data_be_shared'.
    """
    # Fields to display in the user list
    list_display = ('username', 'email', 'age', 'is_staff', 'is_superuser', 'is_active', 'last_login', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'can_be_contacted', 'can_data_be_shared', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Fields displayed when editing/creating a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'age', 'can_be_contacted', 'can_data_be_shared')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Fields displayed when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'email', 'age', 'is_staff', 'is_active'),
        }),
    )

    # Add filtering and grouping by user status
    ordering = ('-date_joined',)


# Optional: Unregister the default Group admin if not needed
admin.site.unregister(Group)
