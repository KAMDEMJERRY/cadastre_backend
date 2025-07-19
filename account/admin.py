from django.contrib import admin

# Register your models here.
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'cni', 'id_cadastrale', 
        'type_proprietaire', 'role', 'is_active', 'date_creation'
    ]
    list_filter = ['type_proprietaire', 'role', 'is_active', 'date_creation']
    search_fields = ['nom', 'prenom', 'email', 'cni', 'id_cadastrale']
    readonly_fields = ['date_creation', 'date_modification', 'date_activation']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'email', 'cni', 'id_cadastrale')
        }),
        ('Paramètres', {
            'fields': ('type_proprietaire', 'role', 'is_active')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification', 'date_activation'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Nom complet'