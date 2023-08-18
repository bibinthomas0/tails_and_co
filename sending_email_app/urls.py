from django.urls import path,include
from sending_email_app import views
urlpatterns = [
    
    path('send_mail_to_all/',views.send_mail_to_all,name='send_mail_to_all'),
    
    
]