from django.shortcuts import render
import random
import json
from django.core.paginator import Paginator, Page
from decimal import Decimal
from datetime import datetime
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, validators
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.contrib import messages
from cust.models import CustomUser, CustomUserManager, Userdetails
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from .models import Product, Subcategory, Category, ProductImage, productcolor
from cart.models import Cart, CartItem, Order, OrderItem, Coupon
from sending_email_app.tasks import send_mail_func,send_mail_order,send_mail_orderstatus
from datetime import date,timedelta
from datetime import datetime, timedelta, timezone

# Create your views here.
def AdminDashboard(request):
    if request.method=='POST':
        from_date_str=request.POST.get('from')
        To_date_str=request.POST.get('to')
        from_date = datetime.strptime(from_date_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        to_date = datetime.strptime(To_date_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    else:  # Make sure to handle the else case to avoid the 'date' variable issue
        from_date = None
        to_date = None
    week_date = datetime.now(timezone.utc) - timedelta(days=7)  # Use timezone.now() for Django's timezone-aware datetime
    month_date = datetime.now(timezone.utc) - timedelta(days=30)
    end_date = datetime.now(timezone.utc)
    weekly = Order.objects.filter(created_at__range=(week_date, end_date))
    monthly = Order.objects.filter(created_at__range=(month_date, end_date))
    total_week_amount=0
    total_month_amount=0
    for dates in weekly:
        total_week_amount+=dates.total_price
    for dates in monthly:
        total_month_amount+=dates.total_price
    context={'weekly':weekly,'monthly':monthly,'total_week_amount':total_week_amount,'total_month_amount':total_month_amount}
    
    return render(request, "admin/dashboard.html",context)


def Adminusers(request):
    data = CustomUser.objects.all()
    context = {"data": data}
    return render(request, "admin/users.html", context)


def block(request, id):
    user = CustomUser.objects.get(id=id)
    if request.method == "POST":
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({"status": "success"})


def Adminlogin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None and (user.is_superuser):
            custom_user_manager = CustomUserManager()
            custom_user_manager.send_otp_email(request, email)
            login(request, user)
            return redirect("adminotp")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "adminlogin.html")


def AddproductT(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        gender = request.POST.get("gender")
        age = request.POST.get("age")
        color = request.POST.get("color")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")
        images = request.FILES.getlist("images")
        category = get_object_or_404(Category, id=category_id)
        subcategory = get_object_or_404(Subcategory, id=subcategory_id)
        product = Product.objects.create(
            name=name,
            description=description,
            stock=stock,
            gender=gender,
            age=age,
            color=color,
            price=price,
            category=category,
            subcategory=subcategory,
        )
        for img in images:
            image = ProductImage.objects.create(product=product, image=img)
            image.save()
    cate = Category.objects.all()
    return render(request, "admin/product.html", {"cate": cate})


def Addproduct(request):
    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")
        category = get_object_or_404(Category, id=category_id)
        subcategory = get_object_or_404(Subcategory, id=subcategory_id)
        Product.objects.create(name=name, category=category, subcategory=subcategory)
        return redirect("addproduct")
    prod = Product.objects.all()
    paginator = Paginator(prod, per_page=6)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    cate = Category.objects.all()
    context = {"cate": cate, "prod": page}
    return render(request, "admin/product.html", context)


def Variations(request, id):
    if request.method == "POST":
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        gender = request.POST.get("gender")
        age = request.POST.get("age")
        color = request.POST.get("color")
        price = request.POST.get("price")
        product = Product.objects.get(id=id)
        pc = productcolor.objects.create(
            product=product,
            description=description,
            stock=stock,
            gender=gender,
            age=age,
            color=color,
            price=price,
        )
        pc.save
        return redirect("variations", id=id)
    pro = productcolor.objects.filter(product_id=id)
    return render(request, "admin/variations.html", {"pro": pro})


def Imagess(request, id):
    if request.method == "POST":
        images = request.FILES.getlist("images")
        pcolor = productcolor.objects.get(id=id)
        product = Product.objects.get(id=pcolor.product_id)
        for img in images:
            image = ProductImage.objects.create(
                color=pcolor, image=img, product=product
            )
        return redirect("imagess", id)
    # pcolor=productcolor.objects.get(id=c_id)
    # product=Product.objects.get(id=p_id)
    pcolor = productcolor.objects.get(id=id)
    product = Product.objects.get(id=pcolor.product_id)
    images = ProductImage.objects.filter(Q(product=product) & Q(color=pcolor))
    return render(request, "admin/image.html", {"images": images})


def Adminregistration(request):
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
        else:
            custom_user_manager = CustomUserManager()
            custom_user_manager.send_otp_email(request, email)
            my_user = CustomUser.objects.create_superuser(
                name=name,
                email=email,
                phone_number=phone_number,
                password=password,
                is_verified=False,
            )
            my_user.save()
            user = authenticate(request, email=email, password=password)
            return redirect("adminotp")
    return render(request, "adminlogin.html")


def Adminotppage(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")
        email = request.session.get("gmail")
        print(user_otp,stored_otp)
        if user_otp == stored_otp:
            edit = CustomUser.objects.get(email=email)
            edit.is_verified = True
            edit.save()
            return redirect("addproduct")
        else:
            return redirect("adminotp")
    return render(request, "otp.html")


def Deleteuser(request, id):
    dd = CustomUser.objects.get(id=id)
    dd.delete()
    return redirect("adminusers")


# category management
def Admincategory(request):
    if request.method == "POST":
        category = request.POST.get("category")
        Category.objects.create(category_name=category)
        return redirect("admincategory")
    cate = Category.objects.all()
    subc = Subcategory.objects.all()
    context = {"cate": cate, "subc": subc}
    return render(request, "admin/category.html", context)


def Addcategory(request):
    if request.method == "POST":
        category = request.POST.get("category")
        Category.objects.create(category_name=category)
        return redirect("admincategory")


def Deletecategory(request, id):
    cat = get_object_or_404(Category, id=id)
    cat.delete()
    return redirect("admincategory")


def Addsubcategory(request):
    if request.method == "POST":
        category_id = request.POST.get("category")
        subcategory = request.POST.get("subcategory")
        category = get_object_or_404(Category, id=category_id)
        Subcategory.objects.create(category=category, subcategory_name=subcategory)
        return redirect("admincategory")


def Deletesubcategory(request, id):
    scat = Subcategory.objects.get(id=id)
    scat.delete()
    return redirect("admincategory")


################################


def Productdelete(request, id):
    cat = Product.objects.get(id=id)
    cat.delete()
    return redirect("addproduct")


def Orders(request):
    orders = Order.objects.all().order_by("-created_at")
    paginator = Paginator(orders, per_page=3)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "orders": page,
    }
    return render(request, "admin/ordermanagement.html", context)


def update_order_status(request, id):
    if request.method == "POST":
        st = request.POST.get("status")
        edit = OrderItem.objects.get(id=id)
        edit.status = st
        edit.save()
        id = edit.order.id
        email=edit.order.user.email
        print(email)
        print(edit.order.address.custom_name)
        try:
            if st=='S': 
                message=f"Good news! {edit.order.address.custom_name}, Your order {edit.product.product.name} has shipped. We will reach you soon✓"
            elif st=='O':
                message=f"Hey {edit.order.address.custom_name}, Your order {edit.product.product.name} has been reached the hub nearest to you, Our delivery partner will reach you as soon as possible "
            elif st=='D':
                message=f"{edit.order.address.custom_name}, Your order {edit.product.product.name} has been succesfully delivered"
            send_mail_orderstatus(request,message,email)
        finally:
            return redirect("adminorder_deatails", id)


def variantedit(request, id):
    if request.method == "POST":
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        gender = request.POST.get("gender")
        age = request.POST.get("age")
        color = request.POST.get("color")
        price = request.POST.get("price")
        edit = productcolor.objects.get(id=id)
        edit.description = description
        edit.stock = stock
        edit.gender = gender
        edit.age = age
        edit.color = color
        edit.price = price
        edit.save()

        return redirect("addproduct")
    pro = productcolor.objects.get(id=id)
    return render(request, "admin/variantedit.html", {"pro": pro})


def deletevariant(request, id):
    d = productcolor.objects.get(id=id)
    d.delete()
    return redirect("addproduct")


def adminlogout(request):
    logout(request)
    return redirect("adminlogin")


def Admincoupon(request):
    if request.method == "POST":
        code = request.POST.get("code")
        discount = request.POST.get("discount")
        minamount = request.POST.get("minamount")
        valid_from_str = request.POST.get("from")
        valid_to_str = request.POST.get("to")
        valid_from = datetime.strptime(valid_from_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        valid_to = datetime.strptime(valid_to_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        Coupon.objects.create(
            code=code,
            minimumamount=minamount,
            discount=discount,
            valid_from=valid_from,
            valid_to=valid_to,
        )
        return redirect("admincoupon")
    datas = Coupon.objects.all()
    return render(request, "admin/coupons.html", {"datas": datas})


def adminorder_deatails(request, id):
    order = Order.objects.get(id=id)
    order_items = OrderItem.objects.filter(order=order)
    try:
        x = Decimal(order.coupon_applied.discount)
        sub_price = order.total_price + x
    except:
        sub_price = order.total_price
    address = Userdetails.objects.get(id=order.address.id)
    context = {
        "order_items": order_items,
        "order": order,
        "sub_price": sub_price,
        "address": address,
    }
    return render(request, "admin/uniqueorder.html", context)


def order_cancel(request, id):
    edit = OrderItem.objects.get(id=id)
    edit.status = "C"
    edit.save()
    id = edit.order.id
    return redirect("adminorder_deatails", id)
def deleteimage(request,id):
    img=ProductImage.objects.get(id=id)
    img.delete()
    id=img.color.id
    return redirect('imagess',id)
from django.views.decorators.csrf import csrf_exempt

def croper(request):
    return render(request,'admin/imagecrop.html')




@csrf_exempt
def cropimage(request):
    print('aaaaaaaaaaaaaaaa')
    if request.method == 'POST':
        print('ddddddddddddddd')
        try:
            data = json.loads(request.body)
            image_data = data.get('image_data')
            print('hhhhhhh')
            # Here, you can process the image_data as needed, such as saving it to a model or file
            # Example: Save the cropped image to a model
            # YourModel.objects.create(image_field=image_data)
            
            # Return a response indicating success
            return JsonResponse({'message': 'Image cropped and saved successfully.'})
        
        except Exception as e:
            print('kkkkkkkkkkkkkkkk')
            return JsonResponse({'error': str(e)}, status=500)
    
def deactivatecoupon(request,id):
    coup=Coupon.objects.get(id=id)
    coup.active=False
    coup.save()
    return redirect('admincoupon')