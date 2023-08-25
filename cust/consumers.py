from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.template.loader import get_template
from django.http import JsonResponse

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