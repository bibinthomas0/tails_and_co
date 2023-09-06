from django.db import models
from cust.models import CustomUser,Userdetails
from owner.models import Product,productcolor,ProductImage
from django.template.defaultfilters import slugify


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    minimumamount=models.IntegerField()
    discount = models.FloatField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    category = models.CharField(max_length=50)
    def __str__(self):
        return self.code
    
    
class Usercoupon(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupon,on_delete=models.CASCADE)
    
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    coupon=models.ForeignKey(Coupon, on_delete=models.DO_NOTHING,null=True,blank=True)
    coin_discount = models.IntegerField(default=0)
    def __str__(self):
        return self.user.name


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(productcolor, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def get_total_price(self):
        return self.product.price * self.quantity
        
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class Address(models.Model):
    custom_name = models.CharField(max_length=50)
    house_name = models.CharField(max_length=50)
    landmark = models.CharField(max_length=30)
    pincode = models.IntegerField()
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    def __str__(self):
        return self.custom_name




class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(Address,on_delete=models.DO_NOTHING)
    total_price=models.DecimalField(max_digits=10, decimal_places=2)
    razor_pay_order_id=models.CharField(max_length=100,null=True,blank=True)
    razor_pay_payment_id=models.CharField(max_length=100,null=True,blank=True)
    razor_pay_payment_signature=models.CharField(max_length=100,null=True,blank=True)
    slug  = models.CharField(max_length=200,null=True,blank=True)
    payment_method = models.CharField(max_length=20)
    coupon_applied=models.ForeignKey(Coupon,on_delete=models.DO_NOTHING,null=True,blank=True)
    coin_discount = models.IntegerField(default=0)
    order_id = models.PositiveBigIntegerField()
    def __str__(self):
        return f"Order {self.pk} for {self.user.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self.user.id) +str(self.created_at))
        return super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(productcolor, on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField(default=0)
    last_update=models.DateTimeField(auto_now=True)
    order_status_choices = [
        ('P', 'Processing'),
        ('S', 'Shipped'),
        ('O', 'Out For Delivery'),
        ('D', 'Delivered'),
        ('C', 'Cancelled'),
        ('R', 'Returning')
    ]
    
    status = models.CharField(max_length=1, choices=order_status_choices, default='P')
    total_itemprice=models.DecimalField(max_digits=10, decimal_places=2)
    order_status_choices = [
        ('P', 'Pending'),
        ('R', 'Recieved'),
    ]
    payment_status = models.CharField(max_length=1, choices=order_status_choices, default='P')
    returnpolicy = models.BooleanField(default=True)
    returnstatus = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"



class Wishlist(models.Model):
    userr = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(productcolor, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.userr)
    
    
from django.db import models

class GuestUser(models.Model):
    identifier = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.identifier

class Gcart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    guest_user = models.ForeignKey(GuestUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart created at {self.created_at} for Guest User {self.guest_user}"


class GcartItem(models.Model):
    cart = models.ForeignKey(Gcart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(productcolor, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def get_total_price(self):
        return self.product.price * self.quantity
        
    def __str__(self):
        return  self.quantity
   
class OrderReturn(models.Model):
    orderitem = models.ForeignKey(OrderItem,on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    return_status_choices = [
        ('P', 'Pending'),
        ('C', 'Collected'),  
        ('R', 'Recieved'),
    ]
    status = models.CharField(max_length=1, choices=return_status_choices, default='P')
    total_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.user)
    
   
class Refund(models.Model):
    orderitem = models.ForeignKey(OrderItem,on_delete=models.CASCADE)
    user= models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.user)
    
class Wallet(models.Model):
    coins = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def update_total_coins(self):
        total_coins = self.wallethistory_set.aggregate(models.Sum('coins'))['coins__sum']
        if total_coins is None:
            total_coins = 0
        self.coins = total_coins
        self.save()


class Wallethistory(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    coins = models.IntegerField(default=0)
    task = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.wallet.user)
    

