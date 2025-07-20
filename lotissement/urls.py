from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LotissementViewSet, BlocViewSet, ParcelleViewSet

router = DefaultRouter()
router.register(r'lotissement', LotissementViewSet)
router.register(r'bloc', BlocViewSet)
router.register(r'parcelle', ParcelleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]