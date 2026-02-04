"""
MPART Notification System

Provides email alerts and notifications for grant matches.
"""

from .email_notifier import EmailNotifier, NotificationManager
from .digest_generator import DigestGenerator

__all__ = ['EmailNotifier', 'NotificationManager', 'DigestGenerator']
