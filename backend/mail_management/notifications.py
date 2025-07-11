import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

logger = logging.getLogger(__name__)

def send_user_notification(user_id, notification_type, data):
    """
    Send real-time notification to a specific user
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}",
                {
                    "type": "send.notification",
                    "data": {
                        "type": notification_type,
                        "timestamp": str(timezone.now()),
                        **data
                    }
                }
            )
            logger.info(f"Notification sent to user {user_id}: {notification_type}")
        else:
            logger.warning("Channel layer not available")
    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {e}")

def send_email_update_notification(user_id, email_id, update_type, details=None):
    """
    Send email update notification
    """
    send_user_notification(user_id, "EMAIL_UPDATE", {
        "email_id": email_id,
        "update_type": update_type,
        "details": details or {}
    })

def send_recommendation_notification(user_id, recommendations_count, recommendations=None):
    """
    Send recommendation notification
    """
    send_user_notification(user_id, "NEW_RECOMMENDATIONS", {
        "count": recommendations_count,
        "recommendations": recommendations or []
    })

def send_classification_notification(user_id, email_id, category_name, confidence=None):
    """
    Send email classification notification
    """
    send_user_notification(user_id, "EMAIL_CLASSIFIED", {
        "email_id": email_id,
        "category": category_name,
        "confidence": confidence
    })

def send_system_notification(user_id, message, level="info"):
    """
    Send system notification
    """
    send_user_notification(user_id, "SYSTEM_NOTIFICATION", {
        "message": message,
        "level": level
    })

def broadcast_to_all_users(notification_type, data):
    """
    Broadcast notification to all connected users
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                "broadcast",
                {
                    "type": "send.notification",
                    "data": {
                        "type": notification_type,
                        "timestamp": str(timezone.now()),
                        **data
                    }
                }
            )
            logger.info(f"Broadcast notification sent: {notification_type}")
        else:
            logger.warning("Channel layer not available for broadcast")
    except Exception as e:
        logger.error(f"Error broadcasting notification: {e}")

# Notification types constants
class NotificationTypes:
    EMAIL_UPDATE = "EMAIL_UPDATE"
    EMAIL_CLASSIFIED = "EMAIL_CLASSIFIED"
    NEW_RECOMMENDATIONS = "NEW_RECOMMENDATIONS"
    SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION"
    EMAIL_MARKED_READ = "EMAIL_MARKED_READ"
    NOTE_ADDED = "NOTE_ADDED"
    CONNECTION_ESTABLISHED = "CONNECTION_ESTABLISHED"
