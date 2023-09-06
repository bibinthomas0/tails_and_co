from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import get_template
from django.http import JsonResponse
import re


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.GROUP_NAME = 'user-notifications'
        async_to_sync(self.channel_layer.group_add)(
            self.GROUP_NAME, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.GROUP_NAME, self.channel_name
        )

    def user_joined(self,event):
        html = get_template('notification.html').render(
            context = {'username' : event["text"]}
            
        )
        self.send(text_data=html)
        
    def coupon_added(self, event):
        print("Coupon added event received:", event)
        html = get_template('notification.html').render(
            context={'coupon_code': event["coupon_code"]}
        )
        self.send(text_data=html)
        
    def custom_notification(self, event):
        print("Custom notification", event)
        html = get_template('notification.html').render(
            context={'coupon_code': event["coupon_code"]}
        )
        self.send(text_data=html)
    

    async def order_notification(self, event):
        print("oderrrr", event)
        html = get_template('notification.html').render(
            context={'coupon_code': event["message"]}
        )
        await self.send(text_data=html)

    async def subscribe_to_user_notifications(self, user_id):
        group_name = f"user-notifications-{user_id}"
        await self.channel_layer.group_add(group_name, self.channel_name)
        
        


class OrderNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope['session'].get('user_id')
        if user_id is not None and isinstance(user_id, int):
            user_id_str = re.sub(r'[^a-zA-Z0-9]', '_', str(user_id))
            group_name = f"user_notifications_{user_id_str}"
            await self.channel_layer.group_add(group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()


    async def disconnect(self, close_code):
        user_id = self.scope['session'].get('user_id')
        if user_id is not None and isinstance(user_id, int):
            user_id_str = re.sub(r'[^a-zA-Z0-9]', '_', str(user_id))
            group_name = f"user_notifications_{user_id_str}"
            await self.channel_layer.group_discard(group_name, self.channel_name)


    async def order_notification(self, event):
        coupon_code = event.get("coupon_code", "")
        html = get_template('notification.html').render(
            context={'coupon_code': coupon_code}
        )
        await self.send(text_data=html)

    async def subscribe_to_user_notifications(self, user_id):
        group_name = f"user-notifications-{user_id}"
        await self.channel_layer.group_add(group_name, self.channel_name)

    async def update_order_status(self, user_id, order_id, new_status):
        # Update the order status here

        # Send a notification to the user
        group_name = f"user-notifications-{user_id}"
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'order_notification',
                'coupon_code': f"Order {order_id} status updated to {new_status}",
            }
        )
