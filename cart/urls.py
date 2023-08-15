from django.urls import path
from . import views
urlpatterns = [
    path('cartdetail', views.CartDetail, name='cartdetail'),
    path('add/<int:id>/', views.CartAdd, name='CartAdd'),
    path('delete/<int:id>/', views.CartRemove, name='delete'),
    path('checkout', views.Checkout, name='checkout'),
    path('createorder', views.create_order, name='createorder'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('removecoupon', views.Removecoupon, name='removecoupon'),
    path('cartaddjs/<int:id>/', views.cartaddjs, name='cartaddjs'),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('thanku/', views.thanku, name='thanku'),
    path('selectaddress', views.selectaddress, name='selectaddress'),
    path('createorders', views.create_orders, name='createorders'),
]
