from django.contrib import admin
from django.utils.html import format_html
from .models import Bloc, Lotissement, Parcelle

@admin.register(Lotissement)
class LotissementAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_address', 'created_at', 'updated_at', 'bloc_count')
    search_fields = ('name', 'addresse', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'addresse', 'description')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def formatted_address(self, obj):
        return obj.addresse if obj.addresse else "Non spécifiée"
    formatted_address.short_description = "Adresse"

    def bloc_count(self, obj):
        return obj.bloc_set.count()
    bloc_count.short_description = "Nombre de blocs"

@admin.register(Bloc)
class BlocAdmin(admin.ModelAdmin):
    list_display = ('name', 'lotissement_link', 'parcelle_count', 'created_at')
    list_select_related = ('lotissement',)
    search_fields = ('name', 'lotissement__name', 'description')
    list_filter = ('lotissement', 'created_at')
    autocomplete_fields = ('lotissement',)
    readonly_fields = ('created_at', 'updated_at')

    def lotissement_link(self, obj):
        return format_html('<a href="/admin/terrain/lotissement/{}/change/">{}</a>',
                          obj.lotissement.id, obj.lotissement.name)
    lotissement_link.short_description = "Lotissement"
    lotissement_link.admin_order_field = 'lotissement__name'

    def parcelle_count(self, obj):
        return obj.parcelle_set.count()
    parcelle_count.short_description = "Nombre de parcelles"

@admin.register(Parcelle)
class ParcelleAdmin(admin.ModelAdmin):
    list_display = ('id', 'bloc_link', 'proprietaire_link', 'superficie', 'perimetre', 'created_at')
    list_select_related = ('bloc__lotissement', 'proprietaire')
    search_fields = ('bloc__name', 'bloc__lotissement__name', 'proprietaire__username')
    list_filter = ('bloc__lotissement', 'bloc', 'created_at')
    autocomplete_fields = ('bloc', 'proprietaire')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('bloc', 'proprietaire')
        }),
        ('Détails techniques', {
            'fields': ('superficie', 'perimetre')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def bloc_link(self, obj):
        return format_html('<a href="/admin/terrain/bloc/{}/change/">{}</a> (Lotissement: {})',
                          obj.bloc.id, obj.bloc.name, obj.bloc.lotissement.name)
    bloc_link.short_description = "Bloc"
    bloc_link.admin_order_field = 'bloc__name'

    def proprietaire_link(self, obj):
        return format_html('<a href="/admin/account/user/{}/change/">{}</a>',
                          obj.proprietaire.id, obj.proprietaire.get_full_name() or obj.proprietaire.username)
    proprietaire_link.short_description = "Propriétaire"
    proprietaire_link.admin_order_field = 'proprietaire__username'