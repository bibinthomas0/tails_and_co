from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from cust.managers import CustomUserManager


class CustomUser(AbstractBaseUser):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=115)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class Userdetails(models.Model):
    userr = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    custom_name = models.CharField(max_length=50)
    house_name = models.CharField(max_length=50)
    landmark = models.CharField(max_length=30)
    pincode = models.IntegerField()
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.custom_name

# class GuestUser(models.Model):
#     identifier = models.CharField(max_length=100, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.identifier