from django.urls import path, include
from django.db import connection
from django.http import JsonResponse
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from modules.accounts.views import CsrfView, LoginView, LogoutView, ProfileView
from modules.applications.views import ApplicationViewSet
from modules.applications.serializers import CompanySerializer, ProductSerializer
from modules.companies.models import Company
from modules.products.models import CreditProduct
from modules.notifications.models import Notification

class Companies(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompanySerializer
    def get_queryset(self):
        if getattr(self,'swagger_fake_view',False): return Company.objects.none()
        return (Company.objects.all() if self.request.user.is_staff else Company.objects.filter(memberships__user=self.request.user)).order_by('id')

class Products(viewsets.ReadOnlyModelViewSet):
    queryset = CreditProduct.objects.all().order_by('id')
    serializer_class = ProductSerializer

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id','application','message','read','created_at']

class Notifications(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    def get_queryset(self):
        if getattr(self,'swagger_fake_view',False): return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)
    @action(detail=True,methods=['post'])
    def read(self,request,pk=None):
        n = self.get_object(); n.read = True; n.save(update_fields=['read'])
        return Response(self.get_serializer(n).data)

def health(request):
    with connection.cursor() as cursor: cursor.execute('SELECT 1')
    return JsonResponse({'status':'ok'})

router = DefaultRouter()
router.register('companies',Companies,basename='company')
router.register('products',Products)
router.register('applications',ApplicationViewSet,basename='application')
router.register('notifications',Notifications,basename='notification')
urlpatterns = [path('health/',health),path('api/v1/',include(router.urls)),path('api/v1/auth/csrf/',CsrfView.as_view()),path('api/v1/auth/login/',LoginView.as_view()),path('api/v1/auth/logout/',LogoutView.as_view()),path('api/v1/auth/me/',ProfileView.as_view()),path('api/schema/',SpectacularAPIView.as_view(),name='schema'),path('api/docs/',SpectacularSwaggerView.as_view(url_name='schema'))]
