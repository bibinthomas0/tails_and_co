from django.shortcuts import render
import random
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, validators
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.contrib import messages
from .models import CustomUser, CustomUserManager, Userdetails
from owner.models import Product, ProductImage, Category, Subcategory, productcolor
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.hashers import make_password
from cart.models import Cart, CartItem, Order, OrderItem, Wishlist


# Create your views here.
def Homepage(request):
    email = request.session.get("gmail")
    if email is not None:
        dd = CustomUser.objects.get(email=email)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        numitems = cart_items.count()
        context = {"numitems": numitems}
        if dd.is_verified == False:
            return redirect("logout")
    data = Product.objects.all()
    ks = ProductImage.objects.all()
    cate = Category.objects.all()
    context = {
        "data": data,
        "ks": ks,
        "cate": cate,
    }
    return render(request, "index.html", context)


def Newaddrersspage(request):
    if request.method == "POST":
        house_name = request.POST.get("hname")
        landmark = request.POST.get("landmark")
        pincode = request.POST.get("pincode")
        city = request.POST.get("city")
        state = request.POST.get("state")
        custom_name = request.POST.get("cname")
        d = request.user
        user = Userdetails.objects.create(
            userr=d,
            custom_name=custom_name,
            house_name=house_name,
            landmark=landmark,
            pincode=pincode,
            city=city,
            state=state,
        )
        user.save()
        return redirect("address")


def Addresspage(request):
    # gmail = request.session.get('gmail')
    # cad=CustomUser.objects.get(email=gmail)
    data = Userdetails.objects.filter(userr=request.user)
    context = {"data": data}
    return render(request, "user/address.html", context)


def addresseditpage(request, id):
    if request.method == "POST":
        house_name = request.POST.get("hname")
        landmark = request.POST.get("landmark")
        pincode = request.POST.get("pincode")
        city = request.POST.get("city")
        state = request.POST.get("state")
        custom_name = request.POST.get("cname")
        edit = Userdetails.objects.get(id=id)
        edit.custom_name = custom_name
        edit.house_name = house_name
        edit.landmark = landmark
        edit.pincode = pincode
        edit.city = city
        edit.state = state
        edit.save()
        return redirect("address")
    data = Userdetails.objects.get(id=id)
    context = {"data": data}
    return render(request, "user/editadress.html", context)


def Profilepage(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")
        user = get_object_or_404(CustomUser, user=request.user)
        id = user.id
        edit = CustomUser.objects.get(id=id)
        edit.email = email
        edit.name = name
        edit.save()
        return redirect("profilec")
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    numitems = cart_items.count()
    d = request.user
    context = {"d": d, "numitems": numitems}
    return render(request, "user/profile.html", context)


def Registerpage(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")
        pass1 = request.POST.get("pass1")
        password = request.POST.get("pass2")
        if pass1 != password or pass1 is None or len(pass1) < 3:
            key = "2"
            messages.error(request, f"Passwords are not matching or week. ({key})")
            return redirect("register")
        if CustomUser.objects.filter(email=email).exists():
            key = "2"
            messages.error(
                request, f"This email address is already registered. ({key})"
            )
            return redirect("register")
        else:
            custom_user_manager = CustomUserManager()
            custom_user_manager.send_otp_email(request, email)
            my_user = CustomUser.objects.create_user(
                name=name,
                email=email,
                phone_number=phone_number,
                password=password,
                is_verified=False,
            )
            my_user.save()
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect("otpp")
    return render(request, "register.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Loginpage(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "login.html")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Otppage(request):
    email = request.session.get("gmail")
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")
        email = request.session.get("gmail")
        if user_otp == stored_otp:
            edit = CustomUser.objects.get(email=email)
            edit.is_verified = True
            edit.save()
            return redirect("home")
        else:
            key = "2"
            messages.error(request, f"invalid otp. ({key})")
            return redirect("otpp")
    context = {"email": email}
    return render(request, "otp.html", context)


def LogoutPage(request):
    edit = get_object_or_404(CustomUser, id=request.user.id)
    edit.is_verified = False
    edit.save()
    logout(request, request.user)
    return redirect("home")


def category(request, id):
    data = Product.objects.filter(category=id)
    cate = Subcategory.objects.filter(category=id)
    context = {
        "data": data,
        "cate": cate,
    }
    return render(request, "category.html", context)


def singleproduct(request, id, aid):
    data = productcolor.objects.get(id=id)
    da = Product.objects.get(id=aid)
    pcolor = productcolor.objects.filter(product=da)
    k = ProductImage.objects.filter(color=data)
    context = {
        "data": data,
        "k": k,
        "pcolor": pcolor,
    }
    return render(request, "singleproduct.html", context)


def changecolor(request, id):
    data = productcolor.objects.get(id=id)
    da = Product.objects.get(productcolor=data)
    pcolor = productcolor.objects.filter(product=da)
    k = ProductImage.objects.filter(color=data)
    context = {
        "data": data,
        "k": k,
        "pcolor": pcolor,
    }
    return render(request, "singleproduct.html", context)


def subcategory(request, c_id, s_id):
    data = Product.objects.filter(category=c_id, subcategory=s_id)
    cate = Subcategory.objects.filter(category=c_id)
    context = {
        "data": data,
        "cate": cate,
    }
    return render(request, "category.html", context)


def forgot(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not CustomUser.objects.filter(email=email).exists():
            key = "2"
            messages.error(request, f"This email address is not registered. ({key})")
            return redirect("forgot")
        else:
            user = CustomUser.objects.get(email=email)
            if user is not None:
                custom_user_manager = CustomUserManager()
                custom_user_manager.send_otp_email(request, email)
                return redirect("forgototp")
    return render(request, "forgot.html")


def forgototp(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")
        if user_otp == stored_otp:
            return redirect("forgotpassword")
        else:
            key = "2"
            messages.error(request, f"invalid otp. ({key})")
            return redirect("forgototp")
    email = request.session.get("gmail")
    context = {"email": email}
    return render(request, "otp.html", context)


def forgotpassword(request):
    if request.method == "POST":
        email = request.session.get("gmail")
        pass1 = request.POST.get("pass1")
        password = request.POST.get("pass2")
        if pass1 == password:
            edit = CustomUser.objects.get(email=email)
            hashed_password = make_password(password)
            edit.password = hashed_password
            edit.save()
            key = "2"
            messages.error(request, f"password successfully changed ({key})")
            return redirect("login")
        else:
            key = "2"
            messages.error(request, f"passwords not matching ({key})")
            return redirect("forgotpassword")
    return render(request, "forgotpassword.html")


def Resendotp(request):
    email = request.session.get("gmail")
    custom_user_manager = CustomUserManager()
    custom_user_manager.send_otp_email(request, email)
    return render(request, "otp.html")


def singproduct(request, id):
    data = productcolor.objects.get(id=id)
    da = Product.objects.get(productcolor=data)
    pcolor = productcolor.objects.filter(product=da)
    k = ProductImage.objects.filter(color=data)
    context = {
        "data": data,
        "k": k,
        "pcolor": pcolor,
    }
    return render(request, "singleproduct.html", context)


def userorders(request):
    cust = get_object_or_404(CustomUser, id=request.user.id)
    orders = Order.objects.filter(user=cust)
    # car = get_object_or_404(Cart, user=request.user)
    # cart_items = CartItem.objects.filter(cart=car)
    # for order in orders:
    #     cart_items = CartItem.objects.filter(cart=car)
    context = {"orders": orders}
    return render(request, "user/orders.html", context)


def wishlist(request):
    user = request.user
    wproducts = Wishlist.objects.filter(userr=user)
    context = {"wproducts": wproducts}
    return render(request, "wishlist.html", context)


def Addwishlist(request, id):
    user = request.user
    product = productcolor.objects.get(id=id)
    Wishlist.objects.create(userr=user, product=product)
    return redirect("singproduct", id)


def Deletewishlist(request, id):
    d = Wishlist.objects.get(id=id)
    d.delete()
    return redirect("wishlist")


def LogoutPage(request):
    edit = get_object_or_404(CustomUser, id=request.user.id)
    edit.is_verified = False
    edit.save()
    logout(request)
    return redirect("home")


def cartaddjs(request, id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(productcolor, id=id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()

    # Add a success message
    response_data = {
        "message": "Product added to cart successfully",
        "product_id": id,
    }

    return JsonResponse(response_data)


# def verify_otp(request):
#     if request.method == 'POST':
#         user_otp = request.POST.get('otp')
#         generated_otp = request.session.get('generated_otp')  # Retrieve from session

#         if user_otp == generated_otp:
#             return redirect('success_page')
#         else:
#             return render(request, 'verify_otp.html', {'error_message': 'Invalid OTP'})

#     return render(request, 'verify_otp.html')
def order_deatails(request,id):
    order=Order.objects.get(id=id)
    order_items=OrderItem.objects.filter(order=order)
    try:
        x=Decimal(order.coupon_applied.discount)
        sub_price = order.total_price + x
    except:
        sub_price = order.total_price
    address=Userdetails.objects.get(id=order.address.id)
    context={'order_items':order_items,'order':order,'sub_price':sub_price,'address':address}
    return render(request, 'user/orderitems.html',context)
def userorder_cancel(request,id):
    edit=OrderItem.objects.get(id=id)
    edit.status='C'
    edit.save()
    id = edit.order.id
    return redirect('order_deatails',id)