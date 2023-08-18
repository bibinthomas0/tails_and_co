from django.http import HttpResponse
from django.shortcuts import render
from sending_email_app.tasks import send_mail_func
# Create your views here.

def send_mail_to_all(request): 
    send_mail_func(request)  
    print('llllllll')
    return HttpResponse("Sent Email Successfully...Check your mail please")
