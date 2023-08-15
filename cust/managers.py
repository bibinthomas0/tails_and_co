from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import random
import pyotp
import secrets
import base64
from twilio.rest import Client
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse

class CustomUserManager(BaseUserManager):
    def create_user(self,name,phone_number, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(name=name,phone_number=phone_number,email=email, **extra_fields)
        extra_fields.setdefault('is_verified', False)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,name, phone_number,email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(name,phone_number,email, password, **extra_fields)
    def send_otp_email(self,request,user_email):
        otp = str(random.randint(100000, 999999)) 
        message = f'Your OTP for verification: {otp}'
        request.session['gmail']=user_email
        request.session['otp'] = otp
        request.session.save()
        send_mail(
            'OTP Verification',
            message,
            'tailsandcorp@gmail.com', 
            [user_email],  
            fail_silently=False,
        )

        return otp
  
   
   # views.py


    def send_otpp(request,phone_number):
        mobile_number = phone_number
        otp =str(random.randint(1000, 9999)) 

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f'Your OTP is: {otp}',
            from_='+12342616521',
            to=mobile_number
        )

        return JsonResponse({'status': 'success', 'otp': otp})



       





