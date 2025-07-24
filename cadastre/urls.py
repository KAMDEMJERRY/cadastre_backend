"""
URL configuration for cadastre project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
   openapi.Info(
      title="API Cadastre",
      default_version='v1',
      description="Description de votre API",
      terms_of_service="https://www.votresite.com/policies/terms/",
      contact=openapi.Contact(email="contact@cadastre.cm"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/login', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/accounts/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/accounts/', include('account.urls')),
    path('api/cadastre/', include('lotissement.urls')),
    # Swagger URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

