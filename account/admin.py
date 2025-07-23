from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'account_type', 'is_active', 'is_staff')
    list_filter = ('account_type', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('genre', 'date_naissance', 'id_cadastrale', 'num_cni', 'addresse', 'num_telephone')}),
        ('Account Type', {'fields': ('account_type', 'domaine', 'nom_organization')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'account_type', 'is_active', 'is_staff')}
        ),
    )
    search_fields = ('email', 'username', 'id_cadastrale', 'num_cni')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Enregistrer le modèle User avec la classe CustomUserAdmin
admin.site.register(User, CustomUserAdmin)