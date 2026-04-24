import logging
from datetime import timedelta

from django.http import Http404
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Monitor
from .serializers import MonitorCreateSerializer, MonitorSerializer

logger = logging.getLogger(__name__)


class MonitorListCreateView(ListCreateAPIView):
    queryset = Monitor.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MonitorCreateSerializer
        return MonitorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        monitor = serializer.save()
        logger.info(f"Monitor '{monitor.id}' registered with timeout={monitor.timeout}s.")
        return Response(
            {
                "message": f"Monitor '{monitor.id}' registered successfully.",
                "monitor": MonitorSerializer(monitor).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MonitorDetailView(RetrieveDestroyAPIView):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return Response(
                {"error": f"No monitor with ID '{kwargs.get('id')}' was found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            monitor = Monitor.objects.get(id=kwargs.get('id'))
        except Monitor.DoesNotExist:
            return Response(
                {"error": f"No monitor with ID '{kwargs.get('id')}' was found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        monitor.delete()
        logger.info(f"Monitor '{kwargs.get('id')}' deleted.")
        return Response(
            {"message": f"Monitor '{kwargs.get('id')}' has been removed successfully."},
            status=status.HTTP_200_OK,
        )


class HeartbeatView(APIView):
    def post(self, request, id):
        try:
            monitor = Monitor.objects.get(id=id)
        except Monitor.DoesNotExist:
            return Response(
                {"error": f"No monitor with ID '{id}' was found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if monitor.status == Monitor.STATUS_DOWN:
            return Response(
                {"error": f"Monitor '{id}' has already gone down. Please register a new monitor to start tracking it again."},
                status=status.HTTP_409_CONFLICT,
            )

        now = timezone.now()
        monitor.expires_at = now + timedelta(seconds=monitor.timeout)
        monitor.last_heartbeat = now
        monitor.status = Monitor.STATUS_ACTIVE
        monitor.save()

        logger.info(f"Heartbeat received for '{id}'. Timer reset to {monitor.timeout}s.")
        return Response(
            {"message": f"Heartbeat received. Timer has been reset to {monitor.timeout} seconds."},
            status=status.HTTP_200_OK,
        )


class PauseView(APIView):
    def post(self, request, id):
        try:
            monitor = Monitor.objects.get(id=id)
        except Monitor.DoesNotExist:
            return Response(
                {"error": f"No monitor with ID '{id}' was found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if monitor.status == Monitor.STATUS_DOWN:
            return Response(
                {"error": f"Monitor '{id}' is already down and cannot be paused."},
                status=status.HTTP_409_CONFLICT,
            )

        if monitor.status == Monitor.STATUS_PAUSED:
            return Response(
                {"message": f"Monitor '{id}' is already paused."},
                status=status.HTTP_200_OK,
            )

        monitor.status = Monitor.STATUS_PAUSED
        monitor.save(update_fields=['status'])

        logger.info(f"Monitor '{id}' paused.")
        return Response(
            {"message": f"Monitor '{id}' has been paused. Send a heartbeat to resume monitoring."},
            status=status.HTTP_200_OK,
        )


