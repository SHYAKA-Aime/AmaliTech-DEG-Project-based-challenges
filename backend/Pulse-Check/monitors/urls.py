from django.urls import path

from .views import HeartbeatView, MonitorDetailView, MonitorListCreateView, PauseView

urlpatterns = [
    path('monitors/', MonitorListCreateView.as_view(), name='monitor-list-create'),
    path('monitors/<str:id>/', MonitorDetailView.as_view(), name='monitor-detail'),
    path('monitors/<str:id>/heartbeat/', HeartbeatView.as_view(), name='monitor-heartbeat'),
    path('monitors/<str:id>/pause/', PauseView.as_view(), name='monitor-pause'),
]
