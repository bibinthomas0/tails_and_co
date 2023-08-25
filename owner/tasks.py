from celery import shared_task
from datetime import datetime, timedelta
from cust.models import CustomUser, CustomUserManager, Userdetails
from .models import Product, Subcategory, Category, ProductImage, productcolor
from cart.models import Cart, CartItem, Order, OrderItem, Coupon,Wishlist,Wallethistory,Refund,OrderReturn
from django.db.models import F, Q, Sum

@shared_task
def expire_coupons():
    current_datetime = datetime.now()
    expired_coupons = Coupon.objects.filter(valid_to__lt=current_datetime)
    for coupon in expired_coupons:
        coupon.update(active=False)
        coupon.save()
    
    
@shared_task
def return_policy():
    expiration_threshold = datetime.now() - timedelta(days=7)
    expired_orders=OrderItem.objects.filter(Q(last_update__lt=expiration_threshold) & Q(status='D'))
    for order in expired_orders:
        order.returnpolicy = False
        order.save()