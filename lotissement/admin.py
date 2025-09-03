from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Lotissement, Bloc, Parcelle, Rue

@admin.register(Lotissement)
class LotissementAdmin(GISModelAdmin):
    list_display = ('name', 'addresse', 'superficie_m2', 'perimetre_m', 'created_at')
    search_fields = ('name', 'addresse')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'addresse', 'description')
        }),
        ('Géométrie', {
            'fields': ('geom', 'longeur', 'superficie_m2', 'perimetre_m')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Bloc)
class BlocAdmin(GISModelAdmin):
    list_display = ('name', 'bloc_lotissement', 'superficie_m2', 'perimetre_m', 'created_at')
    search_fields = ('name', 'bloc_lotissement__name')
    list_filter = ('bloc_lotissement', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'bloc_lotissement', 'description')
        }),
        ('Géométrie', {
            'fields': ('geom', 'longeur', 'superficie_m2', 'perimetre_m')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Parcelle)
class ParcelleAdmin(GISModelAdmin):
    list_display = ('id', 'parcelle_bloc', 'proprietaire', 'superficie_m2', 'created_at')
    search_fields = ('parcelle_bloc__name', 'proprietaire__email')
    list_filter = ('parcelle_bloc', 'proprietaire', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('parcelle_bloc', 'proprietaire')
        }),
        ('Géométrie', {
            'fields': ('geom', 'longeur', 'superficie_m2', 'perimetre_m')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Rue)
class RueAdmin(GISModelAdmin):
    list_display = ('name', 'longeur', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Géométrie', {
            'fields': ('geom', 'longeur', 'superficie_m2', 'perimetre_m')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )