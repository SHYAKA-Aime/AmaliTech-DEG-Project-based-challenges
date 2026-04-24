from django.db import models


class Monitor(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_PAUSED = 'paused'
    STATUS_DOWN = 'down'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PAUSED, 'Paused'),
        (STATUS_DOWN, 'Down'),
    ]

    id = models.CharField(max_length=100, primary_key=True)
    timeout = models.PositiveIntegerField(help_text="Countdown duration in seconds.")
    alert_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    expires_at = models.DateTimeField()
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Monitor({self.id}, status={self.status})"
