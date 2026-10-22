from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI / Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API v1 routes
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/companies/', include('apps.companies.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/applications/', include('apps.applications.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/verification/', include('apps.verification.urls')),
    path('api/v1/scoring/', include('apps.scoring.urls')),
    path('api/v1/decisions/', include('apps.decisions.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/demo/', include('apps.demo.urls')),
]
