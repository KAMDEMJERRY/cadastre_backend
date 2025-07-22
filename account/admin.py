from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.html import format_html

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'email', 'get_full_name', 'account_type', 'num_telephone', 
        'genre', 'is_active', 'date_joined'
    ]
    list_filter = [
        'account_type', 'is_active', 'is_staff', 'is_superuser', 
        'genre', 'date_joined'
    ]
    search_fields = [
        'email', 'first_name', 'last_name', 'num_telephone',
        'num_cni', 'id_cadastrale'
    ]
    readonly_fields = ['date_joined', 'last_login']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {
            'fields': (
                'first_name', 'last_name', 'genre', 'date_naissance',
                'num_telephone', 'num_cni', 'id_cadastrale', 'addresse'
            )
        }),
        ('Type de compte', {
            'fields': ('account_type', 'domaine', 'nom_organization')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'first_name', 'last_name', 'account_type'
            ),
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name or obj.last_name else obj.email
    get_full_name.short_description = 'Nom complet'
    get_full_name.admin_order_field = 'last_name'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['user_permissions'].disabled = True
            
        return form