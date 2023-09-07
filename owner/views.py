from django.shortcuts import render
import random
import json
import calendar
from calendar import monthrange
from django.db import connection
from django.core.paginator import Paginator, Page
from decimal import Decimal
from datetime import datetime
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, validators
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.contrib import messages
from cust.models import CustomUser, CustomUserManager, Userdetails, Usernotification
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from .models import (
    Product,
    Subcategory,
    Category,
    ProductImage,
    productcolor,
    Notifications,
)
from cart.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Coupon,
    OrderReturn,
    Wallet,
    Wallethistory,
    Wishlist,
    Refund,
    Address,
)
from sending_email_app.tasks import (
    send_mail_func,
    send_mail_order,
    send_mail_orderstatus,
)
from datetime import date, timedelta
from datetime import datetime, timedelta, timezone
from cust.signals import custom_notification
from chartjs.views.lines import BaseLineChartView
from django.db.models import Count
from .forms import OrderStatusFilterForm, OrderReturnStatusFilterForm








# Create your views here.
def AdminDashboard(request):
    if request.method == "POST":
        from_date_str = request.POST.get("from")
        To_date_str = request.POST.get("to")
        from_date = datetime.strptime(from_date_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        to_date = datetime.strptime(To_date_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    else:
        from_date = None
        to_date = None
    week_date = datetime.now(timezone.utc) - timedelta(days=7)
    month_date = datetime.now(timezone.utc) - timedelta(days=30)
    year_date = datetime.now(timezone.utc) - timedelta(days=365)
    today = datetime.now(timezone.utc) - timedelta(days=1)
    end_date = datetime.now(timezone.utc)
    weekly = Order.objects.filter(created_at__range=(week_date, end_date))
    monthly = Order.objects.filter(created_at__range=(month_date, end_date))
    yearly = Order.objects.filter(created_at__range=(year_date, end_date))
    daily = Order.objects.filter(created_at__range=(today, end_date))

    total_week_amount = 0
    total_month_amount = 0
    total_year_amount = 0
    total_today_amount = 0
    total_week_orders = 0
    total_month_orders = 0
    total_year_orders = 0
    total_today_orders = 0
    for dates in weekly:
        total_week_amount += dates.total_price
        total_week_orders += dates.items.count()
    for dates in monthly:
        total_month_amount += dates.total_price
        total_month_orders += dates.items.count()
    for dates in yearly:
        total_year_amount += dates.total_price
        total_year_orders += dates.items.count()
    for dates in daily:
        total_today_amount += dates.total_price
        total_today_orders += dates.items.count()
    context = {
        "weekly": weekly,
        "monthly": monthly,
        "total_week_amount": total_week_amount,
        "total_month_amount": total_month_amount,
        "total_year_amount": total_year_amount,
        "total_today_amount": total_today_amount,
        'total_week_orders':total_week_orders,
        'total_month_orders':total_month_orders,
        'total_year_orders':total_year_orders,
        'total_today_orders':total_today_orders
        
    }

    return render(request, "admin/dashboard.html", context)


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
        print(user_otp, stored_otp)
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
    if request.method == "POST":
        search = request.POST.get("search")
        orders = Order.objects.filter(address__custom_name__icontains=search).order_by(
            "-created_at"
        )

    paginator = Paginator(orders, per_page=3)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    try:
        k = f'search results for "{search}"'
        context = {
            "search": k,
            "orders": page,
        }
    except:
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
        email = edit.order.user.email
        try:
            if st == "S":
                message = f"Good news! {edit.order.address.custom_name}, Your order {edit.product.product.name} has been shipped. We will reach you soon✓"
                notif = f"Good news!, Your order '{edit.product.product.name}' has been shipped."

            elif st == "O":
                message = f"Hey {edit.order.address.custom_name}, Your order {edit.product.product.name} has been reached the hub nearest to you, Our delivery partner will reach you as soon as possible "
                notif = f"Hey, Your order '{edit.product.product.name}' with id {edit.order.order_id} is out for delivery,"

            elif st == "D":
                message = f"{edit.order.address.custom_name}, Your order {edit.product.product.name} has been succesfully delivered"
                notif = f"{edit.order.address.custom_name}, Your order {edit.product.product.name} has been succesfully delivered"
            send_mail_orderstatus(request,message,email)
        finally:
            gg = Usernotification.objects.create(user=edit.order.user, content=notif)
            gg.save()
            print(gg.content)
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
        category = request.POST.get("category")
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
            category=category,
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
    address = Address.objects.get(id=order.address.id)
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


def deleteimage(request, id):
    img = ProductImage.objects.get(id=id)
    img.delete()
    id = img.color.id
    return redirect("imagess", id)


from django.views.decorators.csrf import csrf_exempt


def croper(request):
    return render(request, "admin/imagecrop.html")


@csrf_exempt
def cropimage(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image_data = data.get("image_data")

            return JsonResponse({"message": "Image cropped and saved successfully."})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


def deactivatecoupon(request, id):
    coup = Coupon.objects.get(id=id)
    coup.active = False
    coup.save()
    return redirect("admincoupon")


def Returns(request):
    returns = OrderReturn.objects.all().order_by("-created_at")
    paginator = Paginator(returns, per_page=3)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {"returns": page}
    return render(request, "admin/return.html", context)


def returndetails(request, id):
    item = OrderReturn.objects.get(id=id)
    context = {"item": item}
    return render(request, "admin/returndetails.html", context)


def update_return_status(request, id):
    if request.method == "POST":
        st = request.POST.get("status")
        edit = OrderReturn.objects.get(id=id)
        edit.status = st
        edit.save()
        tt = edit.total_price
        if edit.status == "R":
            wallet = Wallet.objects.get(user=edit.user)
            total_coins = wallet.coins
            total_coins += tt
            wallet.coins = total_coins
            wallet.save()
            Wallethistory.objects.create(
                task=f"Product return {edit.orderitem.product.product.name}",
                wallet=wallet,
                coins=edit.total_price,
            )
        return redirect("returndetails", id)


def owner_notifications(request):
    if request.method == "POST":
        content = request.POST.get("notification")
        Notifications.objects.create(content=content)
        return redirect("owner_notifications")
    return render(request, "admin/notifi.html")


def sales_chart_daily(request):
    today = datetime.today()
    past_7_days = [today - timedelta(days=i) for i in range(20)]

    day_labels = [day.strftime("%Y-%m-%d") for day in past_7_days]
    sales_data = Order.objects.filter(
        created_at__date__in=[day.date() for day in past_7_days]
    )

    daily_sales = []
    for day in past_7_days:
        x = sales_data.filter(created_at__date=day.date()).aggregate(
            total=Sum("total_price")
        )["total"]
        day_sales = int(x) if x is not None else 0
        daily_sales.append(day_sales)
        print(x)
        name = "Daily Report"
    context = {
        "name": name,
        "day_labels": day_labels,
        "daily_sales": daily_sales,
        "k": 5,
    }
    return render(request, "admin/chart.html", context)


def sales_chart_weekly(request):
    today = datetime.now(timezone.utc)
    past_weeks = [today - timedelta(weeks=i) for i in range(6, -1, -1)]

    labels = [week.strftime("%Y-%m-%d") for week in past_weeks]

    weekly_sales = []
    for week_start in past_weeks:
        week_end = week_start + timedelta(days=6)
        total_sales = Order.objects.filter(
            created_at__date__range=[week_start.date(), week_end.date()]
        ).aggregate(total=Sum("total_price"))["total"]
        week_sales = int(total_sales) if total_sales is not None else 0
        weekly_sales.append(week_sales)
        print(week_sales)

    context = {
        "name": "Weekly Report",
        "day_labels": labels,
        "daily_sales": weekly_sales,
    }
    return render(request, "admin/chart.html", context)

def sales_chart_monthly(request):
    current_date = datetime.now(timezone.utc)
    current_year = current_date.year
    current_month = current_date.month

    monthly_sales = []
    labels = []

    for i in range(12, -1, -1):
        year = current_year - (i // 12)
        month = (current_month - (i % 12)) % 12 or 12

        month_start = datetime(year, month, 1, tzinfo=timezone.utc)
        month_end = (month_start + timedelta(days=32)).replace(
            day=1, microsecond=0, second=0, minute=0, hour=0
        ) - timedelta(seconds=1)

        labels.append(month_start.strftime("%Y-%m-%d"))

        total_sales = Order.objects.filter(
            created_at__range=(month_start, month_end)
        ).aggregate(total=Sum("total_price"))["total"]
        month_sales = int(total_sales) if total_sales is not None else 0
        monthly_sales.append(month_sales)

    context = {
        "name": "Monthly Report",
        "day_labels": labels,
        "daily_sales": monthly_sales,
    }
    return render(request, "admin/chart.html", context)


def order_filter_view(request):
    form = OrderStatusFilterForm(request.GET)
    if form.is_valid():
        print("hii")
        selected_statuses = [
            field_name for field_name, value in form.cleaned_data.items() if value
        ]
        print(selected_statuses)
        filtered_orderitems = OrderItem.objects.filter(status__in=selected_statuses)

        filtered_orders = []

        for order_item in filtered_orderitems:
            filtered_order = Order.objects.get(id=order_item.order.id)
            filtered_orders.append(filtered_order)
    else:
        filtered_orders = Order.objects.all()
    paginator = Paginator(filtered_orders, per_page=3)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "admin/ordermanagement.html", {"form": form, "orders": page})


def order_return_filter_view(request):
    form = OrderReturnStatusFilterForm(request.GET)
    if form.is_valid():
        print("hii")
        selected_statuses = [
            field_name for field_name, value in form.cleaned_data.items() if value
        ]
        print(selected_statuses)
        filtered_orderitems = OrderReturn.objects.filter(status__in=selected_statuses)
    paginator = Paginator(filtered_orderitems, per_page=3)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "admin/return.html", {"form": form, "returns": page})


def sales_report_btn(request):
    if request.method == "POST":
        valid_from_str = request.POST.get("from")
        valid_to_str = request.POST.get("to")
        valid_from = datetime.strptime(valid_from_str, "%m/%d/%Y")
        valid_to = datetime.strptime(valid_to_str, "%m/%d/%Y")
        y = valid_to - valid_from
    else:
        valid_from = datetime.now()
        valid_to = datetime.now()
        y = timedelta(days=7)

    past_7_days = [valid_to - timedelta(days=i) for i in range(y.days)]

    day_labels = [day.strftime("%Y-%m-%d") for day in past_7_days]
    sales_data = Order.objects.filter(
        created_at__date__in=[day.date() for day in past_7_days]
    )

    daily_sales = []
    for day in past_7_days:
        x = sales_data.filter(created_at__date=day.date()).aggregate(
            total=Sum("total_price")
        )["total"]
        day_sales = int(x) if x is not None else 0
        daily_sales.append(day_sales)
        print(x)

    name = "Daily Report"
    context = {
        "name": name,
        "day_labels": day_labels,
        "daily_sales": daily_sales,
        "k": 5,
    }
    return render(request, "admin/chart.html", context)



def sales_report(request):
    if request.method=='POST':
        from_date_str=request.POST.get('from')
        To_date_str=request.POST.get('to')
        end_date = datetime.now(timezone.utc)
        from_date = datetime.strptime(from_date_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        to_date = datetime.strptime(To_date_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    else: 
        from_date = None
        to_date = None
    end_date = datetime.now(timezone.utc)
    week_date = datetime.now(timezone.utc) - timedelta(days=7) 
    order = Order.objects.filter(created_at__range=(week_date, end_date))
    items = []
    
    for ord in order:
        item = OrderItem.objects.filter(order=ord)
        
        for ite in item:
            items.append(ite)
    context = {
        'order': order,
        'items': items
    }
    return render(request, 'admin/sales_report.html', context)


def sales_monthly(request):
    if request.method=='POST':
        from_date_str=request.POST.get('from')
        To_date_str=request.POST.get('to')
        end_date = datetime.now(timezone.utc)
        from_date = datetime.strptime(from_date_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        to_date = datetime.strptime(To_date_str, "%m/%d/%Y").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    else: 
        from_date = None
        to_date = None
    end_date = datetime.now(timezone.utc)
    month_date = datetime.now(timezone.utc) - timedelta(days=30)
    order = Order.objects.filter(created_at__range=(month_date, end_date))
    items = []
    
    for ord in order:
        item = OrderItem.objects.filter(order=ord)
        
        for ite in item:
            items.append(ite)
    context = {
        'order': order,
        'items': items
    }
    return render(request, 'admin/sales_report.html', context)

def sales_daily(request):
    if request.method == 'POST':
        from_date_str = request.POST.get('fromDate')
        to_date_str = request.POST.get('toDate')

        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").strftime(
             "%Y-%m-%d %H:%M:%S"
        )
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    else: 
        from_date = None
        to_date = None
    orders = Order.objects.filter(created_at__range=(from_date, to_date))

    items = OrderItem.objects.filter(order__in=orders)
    
    context = {
        'order': orders,
        'items': items
    }
    
    return render(request, 'admin/sales_report.html', context)
def deletecoupon(request,id):
    coup = Coupon.objects.get(id=id)
    coup.delete()
    return redirect('admincoupon')