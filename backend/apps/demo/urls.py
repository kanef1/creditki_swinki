from django.urls import path
from .views import DemoResetDataView, DemoScenariosInfoView, DemoQuickLoginView

app_name = 'demo'

urlpatterns = [
    path('reset/', DemoResetDataView.as_view(), name='demo_reset'),
    path('scenarios/', DemoScenariosInfoView.as_view(), name='demo_scenarios'),
    path('quick-login/', DemoQuickLoginView.as_view(), name='demo_quick_login'),
]
