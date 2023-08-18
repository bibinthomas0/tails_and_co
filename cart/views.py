from cart.models import Cart, CartItem, Coupon, Usercoupon
from owner.models import Product, productcolor
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
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect("cartdetail")


def CartDetail(request):
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

    total_stock = sum(item.product.stock for item in cart_items)
    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "total_stock": total_stock,
        "numitems": numitems,
        "cart": cart,
        "subtotal": subtotal,
    }
    return render(request, "cartdetail.html", context)


def Checkout(request):
    address = Userdetails.objects.filter(userr=request.user).order_by("-created_at")
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    k = 15
    total_price = (
        int(sum((item.product.price * item.quantity for item in cart_items))) + k
    )

    subtotal = total_price
    dis = 0
    if cart.coupon is not None:
        coup = get_object_or_404(Coupon, id=cart.coupon.id)
        dis = coup.discount
        total_price -= dis
    numitems = cart_items.count()
    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
    payment = client.order.create(
        {"amount": total_price * 100, "currency": "INR", "payment_capture": 1}
    )
    print(payment)
    context = {
        "address": address,
        "cart_items": cart_items,
        "total_price": total_price,
        "numitems": numitems,
        "dis": dis,
        "subtotal": subtotal,
        "payment": payment,
    }
    return render(request, "checkout.html", context)


@login_required
def create_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    total_price = Decimal(0)
    add = request.session.get("selected_address")
    payment1 = request.session.get("pay-method")
    address = get_object_or_404(Userdetails, id=add)
    for cart_item in cart.items.all():
        total_price += cart_item.product.price * cart_item.quantity
    try:
        coup = get_object_or_404(Coupon, id=cart.coupon.id)
        dis = coup.discount
        di = Decimal(dis)
        total_price -= di
        total_price_float = float(total_price)
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_method=payment1,
            coupon_applied=coup,
        )
    except:
        total_price_float = float(total_price)
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_method=payment1,
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
    cart.coupon = None
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


from django.http import JsonResponse


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


def cartaddjs(request, id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(productcolor, id=id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()

    # Add a success message
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
        if 1 <= quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            if cart.coupon is not None:
                print("hhhhhhhh")
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


def create_orders(request):
    cart = get_object_or_404(Cart, user=request.user)
    total_price = Decimal(0)
    add = request.session.get("selected_address")
    payment1 = request.session.get("pay-method")
    address = get_object_or_404(Userdetails, id=add)
    for cart_item in cart.items.all():
        total_price += cart_item.product.price * cart_item.quantity
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
        )
    except:
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_method=payment1,
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
    cart.coupon = None
    cart.save()
    return render(request, "thanku.html")
