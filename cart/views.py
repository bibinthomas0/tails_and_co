from cart.models import (
    Cart,
    CartItem,
    Coupon,
    Usercoupon,
    Gcart,
    GcartItem,
    GuestUser,
    Userdetails,
    Address,
    Wallet,
    Wallethistory,
)
from owner.models import Product, productcolor,Category
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from cust.models import Userdetails, CustomUser
from .models import Order, OrderItem
from decimal import Decimal
from django.contrib import messages
from django.urls import reverse
from django.db.models import F, Q, Sum
from django.http import JsonResponse
import razorpay
from django.conf import settings
from sending_email_app.tasks import send_mail_func, send_mail_order
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import random


def CartAdd(request, id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(productcolor, id=id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    bag = CartItem.objects.all()
    return redirect("singproduct", id)


def CartRemove(request, id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(productcolor, id=id)
    cart.coin_discount = 0
    cart.save()
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect("cartdetail")


def CartDetail(request):
    if request.user.is_authenticated:
        cart, create = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        numitems = cart_items.count()
        cart_items = cart_items.annotate(
            total_product_price=F("product__price") * F("quantity")
        )
        total_price = cart_items.aggregate(Sum("total_product_price"))[
            "total_product_price__sum"
        ]
        subtotal = total_price
        if cart.coupon is not None:
            coup = get_object_or_404(Coupon, id=cart.coupon.id)
            k = coup.discount
            dis = Decimal(k)
            total_price -= dis
        coupons = Coupon.objects.all()
        print(coupons)
        total_stock = sum(item.product.stock for item in cart_items)
    else:
        session_id = request.session.session_key
        if session_id is not None:
            print(session_id)
        else:
            request.session.save()
            session_id = request.session.session_key
            print("hs    ", session_id)
        guser, create = GuestUser.objects.get_or_create(identifier=session_id)
        cart, create = Gcart.objects.get_or_create(guest_user=guser)
        cart_items = GcartItem.objects.filter(cart=cart)
        numitems = cart_items.count()
        cart_items = cart_items.annotate(
            total_product_price=F("product__price") * F("quantity")
        )
        total_price = cart_items.aggregate(Sum("total_product_price"))[
            "total_product_price__sum"
        ]
        subtotal = total_price

        coupons = Coupon.objects.all()
        print(coupons)
        total_stock = sum(item.product.stock for item in cart_items)
    print(request.user)
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_stock": total_stock,
        "numitems": numitems,
        "cart": cart,
        "subtotal": subtotal,
        "coupons": coupons,
    }
    return render(request, "cartdetail.html", context)


@login_required(login_url="login")
def Checkout(request):
    address = Userdetails.objects.filter(userr=request.user).order_by("-created_at")
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    coins = cart.coin_discount
    k = 15
    # cart.coin_discount=0
    # cart.save()
    total_price = (
        int(sum((item.product.price * item.quantity for item in cart_items))) + k
    )
    subtotal = total_price
    total_price -= coins
    dis = 0
    if cart.coupon is not None:
        coup = get_object_or_404(Coupon, id=cart.coupon.id)
        dis = coup.discount
        total_price -= dis

    numitems = cart_items.count()
    print(total_price, coins)
    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
    payment = client.order.create(
        {"amount": total_price * 100, "currency": "INR", "payment_capture": 1}
    )

    coin = Wallet.objects.get(user=request.user)
    coin_available = coin.coins
    cn = (total_price // 100) * 30
    wallet = Wallet.objects.get(user=request.user)
    if wallet.coins < cn:
        cn = wallet.coins
    request.session["coinss"] = cn
    context = {
        "cart": cart,
        "address": address,
        "cart_items": cart_items,
        "total_price": total_price,
        "numitems": numitems,
        "dis": dis,
        "subtotal": subtotal,
        "payment": payment,
        "coin_available": coin_available,
        "cn": cn,
    }
    return render(request, "checkout.html", context)


def coin_add(request):
    cn = request.session.get("coinss")
    cart = get_object_or_404(Cart, user=request.user)
    if cart.coin_discount > 0:
        cart.coin_discount = 0
    else:
        cart.coin_discount = cn
    cart.save()
    return redirect("checkout")


@login_required
def create_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    total_price = Decimal(0)
    add = request.session.get("selected_address")
    payment1 = request.session.get("pay-method")
    ad = get_object_or_404(Userdetails, id=add)
    address = Address.objects.create(
        custom_name=ad.custom_name,
        city=ad.city,
        landmark=ad.landmark,
        pincode=ad.pincode,
        house_name=ad.house_name,
        state=ad.state,
    )
    for cart_item in cart.items.all():
        total_price += cart_item.product.price * cart_item.quantity
    k = 15
    total_price -= cart.coin_discount
    total_price += k
    try:
        coup = get_object_or_404(Coupon, id=cart.coupon.id)
        dis = coup.discount
        di = Decimal(dis)
        total_price -= di
        total_price_float = float(total_price)
        order_id = str(random.randint(10000000, 99999999))
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_method=payment1,
            coupon_applied=coup,
            order_id=order_id,
            coin_discount=cart.coin_discount,
        )
    except:
        total_price_float = float(total_price)
        order_id = str(random.randint(10000000, 99999999))
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_method=payment1,
            order_id=order_id,
            coin_discount=cart.coin_discount,
        )
    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
    payment = client.order.create(
        {
            "amount": int(total_price_float * 100),
            "currency": "INR",
            "payment_capture": 1,
        }
    )
    order.razor_pay_payment_id = payment["id"]
    order.save()
    print(payment["id"])
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            total_itemprice=cart_item.product.price * cart_item.quantity,
        )
    for cart_item in cart.items.all():
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()
    message = "Order placed successfully"
    send_mail_order(request, message)
    cart.items.all().delete()
    wallet = Wallet.objects.get(user=request.user)
    j = cart.coin_discount
    wallet.coins -= j
    wallet.save()
    if j != 0:
        history = f"Coins Used for Order:{j}"
        Wallethistory.objects.create(wallet=wallet, task=history, coins=j)
    cart.coupon = None
    cart.coin_discount = 0
    cart.save()
    return render(request, "thanku.html")


def create_orders(request):
    cart = get_object_or_404(Cart, user=request.user)
    total_price = Decimal(0)
    add = request.session.get("selected_address")
    payment1 = request.session.get("pay-method")
    ad = get_object_or_404(Userdetails, id=add)
    address = Address.objects.create(
        custom_name=ad.custom_name,
        city=ad.city,
        landmark=ad.landmark,
        pincode=ad.pincode,
        house_name=ad.house_name,
        state=ad.state,
    )
    order_id = str(random.randint(10000000, 99999999))
    for cart_item in cart.items.all():
        total_price += cart_item.product.price * cart_item.quantity
    k = 15
    total_price -= cart.coin_discount
    total_price += k
    try:
        coup = get_object_or_404(Coupon, id=cart.coupon.id)
        dis = coup.discount
        di = Decimal(dis)
        total_price -= di
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_method=payment1,
            coupon_applied=coup,
            order_id=order_id,
            coin_discount=cart.coin_discount,
        )
    except:
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_method=payment1,
            order_id=order_id,
            coin_discount=cart.coin_discount,
        )
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            total_itemprice=cart_item.product.price * cart_item.quantity,
        )
    for cart_item in cart.items.all():
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()
    message = "Order placed successfully"
    send_mail_order(request, message)
    cart.items.all().delete()
    wallet = Wallet.objects.get(user=request.user)
    j = cart.coin_discount
    wallet.coins -= j
    wallet.save()
    if j != 0:
        history = f"Coins Used for Order:{j}"
        Wallethistory.objects.create(wallet=wallet, task=history, coins=j)
    cart.coupon = None
    cart.coin_discount = 0
    cart.save()
    return render(request, "thanku.html")


def orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by("-created_at")
    return render(request, "orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = Order.objects.get(pk=order_id, user=request.user)
    return render(request, "order_detail.html", {"order": order})



def update_cart_item_quantity(request):
    if request.method == "POST":
        cart_item_id = request.POST.get("cart_item_id")
        quantity = int(request.POST.get("quantity"))

        try:
            cart_item = CartItem.objects.get(pk=cart_item_id)
            cart_item.quantity = quantity
            cart_item.save()

            total_price = cart_item.get_total_price()

            return JsonResponse(
                {
                    "status": "success",
                    "quantity": cart_item.quantity,
                    "total_price": total_price,
                }
            )
        except CartItem.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Cart item not found."})


@login_required(login_url="guest_cart_add")
def cartaddjs(request, id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(productcolor, id=id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    cartdetail_url = reverse("cartdetail")
    product_link = f'<a href="{cartdetail_url}">Go to cart</a>'
    success_message = f"Item added to Cart..{product_link}"

    return JsonResponse({"success": success_message})


def guest_cart_add(request, id):
    session_id = request.session.session_key
    if session_id is None:
        request.session.save()
        session_id = request.session.session_key
    guser, created = GuestUser.objects.get_or_create(identifier=session_id)
    gcart, created = Gcart.objects.get_or_create(guest_user=guser)
    product = get_object_or_404(productcolor, id=id)
    gcart_item, created = GcartItem.objects.get_or_create(cart=gcart, product=product)
    gcart_item.quantity += 1
    gcart_item.save()

    cartdetail_url = reverse("cartdetail")
    product_link = f'<a href="{cartdetail_url}">Go to cart</a>'
    success_message = f"Item added to Cart..{product_link}"

    return JsonResponse({"success": success_message})


@csrf_exempt
@require_POST
def update_cart_quantity(request):
    if request.method == "POST":
        id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 0))
        cart_item = get_object_or_404(CartItem, id=id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.coin_discount = 0
        cart.save()
        if 1 <= quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            if cart.coupon is not None:
                cart_items = CartItem.objects.filter(cart=cart)
                cart_items = cart_items.annotate(
                    total_product_price=F("product__price") * F("quantity")
                )
                total_price = cart_items.aggregate(Sum("total_product_price"))[
                    "total_product_price__sum"
                ]
                cou = get_object_or_404(Coupon, id=cart.coupon.id)
                print(cou.minimumamount)
                print(total_price)
                if total_price < cou.minimumamount:
                    return redirect("removecoupon")
            message = "Cart quantity updated successfully."
            return JsonResponse({"success": True, "message": message})
        else:
            return JsonResponse({"success": False, "error": "Invalid quantity"})


@login_required(login_url="login")
def apply_coupon(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    numitems = cart_items.count()
    cart_items = cart_items.annotate(
        total_product_price=F("product__price") * F("quantity")
    )
    total_price = cart_items.aggregate(Sum("total_product_price"))[
        "total_product_price__sum"
    ]
    response_data = {}
    if request.method == "POST":
        code = request.POST.get("code")
        coup = Coupon.objects.get(code=code)
        k = coup.minimumamount
        if Usercoupon.objects.filter(Q(coupon=coup) & Q(user=request.user)).exists():
            response_data = {
                "success": False,
                "message": "already claimed.",
            }
        elif k > total_price:
            response_data = {
                "success": False,
                "message": f"Minimum cart amount ₹{k}.",
            }
        elif not CartItem.objects.filter(cart=cart,product__product__category=coup.category).exists() and coup.category!='2':
            category = Category.objects.get(id=coup.category)
            response_data = {
                "success": False,
                "message": f"Add {category.category_name} to redeem.",
            }

        elif coup.active == False:
            response_data = {
                "success": False,
                "message": "coupon expired.",
            }
        else:
            cart.coupon = coup
            cart.save()
            user = get_object_or_404(CustomUser, id=request.user.id)
            Usercoupon.objects.create(user=user, coupon=coup)
            code = get_object_or_404(Coupon, id=cart.coupon.id)
            x = code.discount
            discount = Decimal(x)
            total_price -= discount
            response_data = {
                "success": True,
                "message": "Coupon applied successfully",
                "coupon_discount": code.discount if cart.coupon else 0,
            }
    return JsonResponse(response_data)


def Removecoupon(request):
    cart = get_object_or_404(Cart, user=request.user)
    usercoupon = Usercoupon.objects.get(Q(coupon=cart.coupon) & Q(user=request.user))
    usercoupon.delete()
    cart.coupon = None
    cart.save()
    return redirect("cartdetail")


def thanku(request):
    return render(request, "thanku.html")


def selectaddress(request):
    if request.method == "POST":
        add = request.POST.get("address")
        paymen = request.POST.get("pay-method")
        print(paymen)
        request.session["selected_address"] = add
        request.session["pay-method"] = paymen
        if paymen != "Upi":
            return redirect("thanku")
        return JsonResponse({"message": "Order placed successfully"})

    return JsonResponse({"message": "Invalid request method"})
