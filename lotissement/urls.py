from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LotissementViewSet, BlocViewSet, ParcelleViewSet
from lotissement import views

router = DefaultRouter()
router.register(r'lotissement', LotissementViewSet)
router.register(r'bloc', BlocViewSet)
router.register(r'parcelle', ParcelleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # API pour les statistiques des lotissements
    path('lotissements/stats/', views.LotissementStatsListView.as_view(), name='lotissement-stats'),
    path('lotissements/<int:pk>/stats/', views.LotissementDetailView.as_view(), name='lotissement-detail-stats'),
    path('lotissements/<int:lotissement_id>/stats-detail/', views.lotissement_stats_detail, name='lotissement-stats-detail'),
    
    # API pour les statistiques des blocs
    path('blocs/stats/', views.BlocStatsListView.as_view(), name='bloc-stats'),
    path('blocs/<int:bloc_id>/stats/', views.bloc_stats_detail, name='bloc-stats-detail'),
    
    # API pour les statistiques globales
    path('stats/globales/', views.global_stats, name='global-stats'),
]