import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if isinstance(self.user, AnonymousUser):
            logger.warning("Anonymous user attempted WebSocket connection")
            await self.close()
        else:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            # Send welcome message
            await self.send(text_data=json.dumps({
                'type': 'CONNECTION_ESTABLISHED',
                'message': 'Real-time notifications connected',
                'user_id': self.user.id
            }))

            logger.info(f"WebSocket connected for user {self.user.id}")

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"WebSocket disconnected for user {self.user.id}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'PING':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'PONG',
                    'timestamp': data.get('timestamp')
                }))
            elif message_type == 'REQUEST_STATUS':
                # Send current status
                status = await self.get_user_status()
                await self.send(text_data=json.dumps({
                    'type': 'STATUS_UPDATE',
                    'data': status
                }))
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            logger.error("Invalid JSON received in WebSocket")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def send_notification(self, event):
        """Send notification to WebSocket"""
        try:
            await self.send(text_data=json.dumps(event['data']))
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    async def email_update(self, event):
        """Handle email update notifications"""
        await self.send(text_data=json.dumps({
            'type': 'EMAIL_UPDATE',
            'data': event['data']
        }))

    async def recommendation_update(self, event):
        """Handle recommendation update notifications"""
        await self.send(text_data=json.dumps({
            'type': 'RECOMMENDATION_UPDATE',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_user_status(self):
        """Get current user status"""
        from .models import Email

        try:
            total_emails = Email.objects.filter(user=self.user).count()
            unread_emails = Email.objects.filter(user=self.user, is_read=False).count()
            high_priority = Email.objects.filter(user=self.user, priority='H').count()

            return {
                'total_emails': total_emails,
                'unread_emails': unread_emails,
                'high_priority_emails': high_priority,
                'last_updated': str(timezone.now())
            }
        except Exception as e:
            logger.error(f"Error getting user status: {e}")
            return {}
