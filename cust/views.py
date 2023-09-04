# from audioop import reverse
from django.shortcuts import render
import random
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, validators
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
from cart.models import Address
from .models import CustomUser, CustomUserManager, Userdetails,Usernotification
from owner.models import Product, ProductImage, Category, Subcategory, productcolor
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.hashers import make_password
from cart.models import Cart, CartItem, Gcart, GcartItem, GuestUser, Order, OrderItem, Wishlist,Wallet,Wallethistory,Refund,OrderReturn
from datetime import date,timedelta
from datetime import datetime, timedelta, timezone
import pdfkit
from xhtml2pdf import pisa
from django.template.loader import get_template
config =  pdfkit.configuration(wkhtmltopdf=r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
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
    notifi = None
    try:
        notifi = Usernotification.objects.filter(user=request.user).order_by('-created_at')
    except:
        notifi = None
    context = {
        "data": data,
        "ks": ks,
        "cate": cate,
       'notifi': notifi
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

@login_required(login_url='login')
def Addresspage(request):
    data = Userdetails.objects.filter(userr=request.user)
    context = {"data": data}
    return render(request, "user/address.html", context)

@login_required(login_url='login')
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

@login_required(login_url='login')
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
        edit.phone_number=phone_number
        edit.save()
        return redirect("profilec")
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    numitems = cart_items.count()
    d = request.user
    try:
        wallet=Wallet.objects.get(user=d)
        wallethistory=Wallethistory.objects.filter(wallet=wallet).order_by('-created_at')
    except:
        wallet=Wallet.objects.create(user=d)
        wallethistory=None
    context = {"d": d, "numitems": numitems,'wallet':wallet,'wallethistory':wallethistory}
    return render(request, "user/profile.html", context)


def Registerpage(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")
        pass1 = request.POST.get("pass1")
        password = request.POST.get("pass2")
        s_id = request.session.session_key
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
            request.session['s_id']==s_id
            return redirect("otpp")
    return render(request, "register.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Loginpage(request):
    print(request.session.session_key)
    
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            request.session['user_id'] = user.id
            s_id = request.session.session_key
            print("---",s_id)
            login(request, user)
            try:
                wallet = Wallet.objects.get(user=request.user)
            except:
                Wallet.objects.create(user=request.user)
            try:
                gt = GuestUser.objects.get(identifier=s_id)
                return redirect('gtouser',s_id)
            except:
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
            s_id = request.session.get('s_id')
            try:
                gt = GuestUser.objects.get(identifier=s_id)
                return redirect('gtouser',s_id)
            except:
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
    try:
        w=Wishlist.objects.get(product=data)
        context = {
            "data": data,
            "k": k,
            "pcolor": pcolor,
            'w':w
        }
    except:
        context = {
            "data": data,
            "k": k,
            "pcolor": pcolor,
        }
        
    return render(request, "singleproduct.html", context)

@login_required(login_url='login')
def userorders(request):
    cust = get_object_or_404(CustomUser, id=request.user.id)
    orders = Order.objects.filter(user=cust).order_by('-created_at')
    context = {"orders": orders}
    return render(request, "user/orders.html", context)

@login_required(login_url='login')
def wishlist(request):
    user = request.user
    wproducts = Wishlist.objects.filter(userr=user)
    context = {"wproducts": wproducts}
    return render(request, "wishlist.html", context)

@login_required(login_url='login')
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
#         generated_otp = request.session.get('generated_otp')  

#         if user_otp == generated_otp:
#             return redirect('success_page')
#         else:
#             return render(request, 'verify_otp.html', {'error_message': 'Invalid OTP'})

#     return render(request, 'verify_otp.html')


@login_required(login_url='login')
def order_deatails(request,id):
    order=Order.objects.get(id=id)
    order_items=OrderItem.objects.filter(order=order)
    try:
        x=Decimal(order.coupon_applied.discount)
        sub_price = order.total_price + x
    except:
        sub_price = order.total_price
    address=Address.objects.get(id=order.address.id)
    date=datetime.now(timezone.utc)
    context={'order_items':order_items,'order':order,'sub_price':sub_price,
             'address':address,'date':date}
    return render(request, 'user/orderitems.html',context)

def userorder_cancel(request,id):
    edit=OrderItem.objects.get(id=id)
    edit.status='C'
    edit.save()
    tt = edit.total_itemprice
    wallet = Wallet.objects.get(user=request.user)
    total_coins=wallet.coins
    total_coins += tt
    wallet.coins = total_coins 
    wallet.save()
    Wallethistory.objects.create(task=f"Product cancel {edit.product.product.name}",wallet=wallet,coins=edit.total_itemprice)
    id = edit.order.id
    return redirect('order_deatails',id)


def searchproduct(request):
    name=request.GET.get('name')
    products=[]
    if name:
        pro=Product.objects.get(name__icontains=name)
        products=productcolor.objects.filter(product=pro)
    context={'name':name,'products':products}
    return render(request,'search.html',context)


def product_return(request,id):
    orderitem=OrderItem.objects.get(id=id)
    orderitem.returnstatus = True
    orderitem.save()
    try:
        c = orderitem.order.coupon_applied
        order = OrderItem.objects.filter(order=orderitem.order)
        count = order.count()
        k = 15
        first = c.discount//count
        fi = Decimal(first)
        total_price= orderitem.total_itemprice - fi + k
        print(total_price)
    except:
        k = 15
        total_price =orderitem.total_itemprice + k
    finally:
        OrderReturn.objects.create(orderitem=orderitem,user=request.user,total_price=total_price)
        id = orderitem.order.id
    return redirect('order_deatails',id)

def tryy(request):
    return render(request,'try.html')

def invoice(request):
    id =96
    order = Order.objects.get(id=id)
    orderitems = OrderItem.objects.filter(order = order)
    if order.coupon_applied:
        t = order.total_price
        c = order.coupon_applied.discount
        c = Decimal(c)
        total = t + c
        print(total)
    else:
        total = order.total_price
    context = {'order':order,'orderitems':orderitems, 'total':total}
    return render(request,'user/invoice.html',context)


from django.shortcuts import get_object_or_404

def gtouser(request,s_id):
    print('hii')
    print(s_id)
    try:
        guser = GuestUser.objects.get(identifier=s_id)
        gcart = Gcart.objects.get(guest_user=guser)
        print("not")
    except GuestUser.DoesNotExist:
        print('qa')
        guser = None
        gcart = None

    cart, create = Cart.objects.get_or_create(user=request.user)
    
    if gcart:
        gcart_items = GcartItem.objects.filter(cart=gcart)
        for gcart_item in gcart_items:
            # Use get_or_create to update quantity if the same product already exists in the user's cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=gcart_item.product,
                defaults={'quantity': gcart_item.quantity}
            )
            if not created:
                cart_item.quantity += gcart_item.quantity
                cart_item.save()

        guser.delete()
    
    cart.save()  # Save the user's cart to update changes

    return redirect('home')

def changepassword(request):
    if request.method == "POST":
        cpass = request.POST.get('cpass')
        pass1 = request.POST.get('pass1')
        email = request.user.email
        user = authenticate(email=email,password=cpass)
        if user is not None:
            new = make_password(pass1)
            user.set_password(pass1)
            user.save()
            key = "2"
            messages.error(
                request, f"Password changed succesfully. Please login to continue. ({key})"
            )
            return redirect('login')
        else:
            key = "2"
            messages.error(
                request, f"Incoorrect current password. ({key})"
            )
            return redirect('changepassword')
    return render(request, "user/changepassword.html")



def render_to_pdf(template_path, context_dict):
    template = get_template(template_path)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="tails invoice.pdf"'

    pisa_status = pisa.CreatePDF(
        html, dest=response
    )

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def generate_invoice(request,id):
    order = Order.objects.get(id=id)
    orderitems = OrderItem.objects.filter(order = order)
    if order.coupon_applied:
        t = order.total_price
        c = order.coupon_applied.discount
        c = Decimal(c)
        total = t + c
        print(total)
    else:
        total = order.total_price
    context = {'order':order,'orderitems':orderitems ,'total':total}
    pdf = render_to_pdf('user/invoice.html', context)

    # Set content type and headers for download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    return response

def Addressdelete(request, id):
    cat = Userdetails.objects.get(id=id)
    cat.delete()
    return redirect("address")