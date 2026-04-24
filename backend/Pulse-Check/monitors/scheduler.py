import json
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone='UTC')


def check_expired_monitors():
    from django.utils import timezone
    from .models import Monitor

    now = timezone.now()
    expired = Monitor.objects.filter(status=Monitor.STATUS_ACTIVE, expires_at__lte=now)

    for monitor in expired:
        monitor.status = Monitor.STATUS_DOWN
        monitor.save(update_fields=['status'])

        alert = {
            "ALERT": f"Device {monitor.id} is down!",
            "time": now.isoformat(),
            "alert_email": monitor.alert_email,
        }
        logger.critical(json.dumps(alert))
        print(f"\n[ALERT] {json.dumps(alert, indent=2)}\n", flush=True)

        send_mail(
            subject=f"[CritMon] Device {monitor.id} is down!",
            message=(
                f"ALERT: Device '{monitor.id}' has stopped sending heartbeats.\n\n"
                f"Last seen: {monitor.last_heartbeat or 'never'}\n"
                f"Time of alert: {now.isoformat()}\n"
            ),
            from_email=None,
            recipient_list=[monitor.alert_email],
            fail_silently=True,
        )


def start():
    if not scheduler.running:
        scheduler.add_job(
            check_expired_monitors,
            trigger='interval',
            seconds=5,
            id='check_expired_monitors',
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Watchdog scheduler started.")
