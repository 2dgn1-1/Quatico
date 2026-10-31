from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, SignUpForm
from .models import Category, Order, OrderItem, Product


def _cart_items(request):
    cart = request.session.get("cart", {})
    products = Product.objects.filter(pk__in=[int(k) for k in cart])
    items, total = [], Decimal("0")
    for p in products:
        qty = cart[str(p.pk)]
        sub = p.price * qty
        total += sub
        items.append({"product": p, "qty": qty, "subtotal": sub})
    return items, total


def home(request):
    products = Product.objects.select_related("category")
    q = request.GET.get("q", "").strip()
    slug = request.GET.get("category", "")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if slug:
        products = products.filter(category__slug=slug)
    return render(request, "shop/home.html", {
        "products": products, "categories": Category.objects.all(), "q": q, "active": slug,
    })


def product_detail(request, slug):
    return render(request, "shop/product.html", {"product": get_object_or_404(Product, slug=slug)})


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get("cart", {})
    try:
        qty = max(1, min(int(request.POST.get("qty", 1)), 20))
    except ValueError:
        qty = 1
    new_qty = min(cart.get(str(pk), 0) + qty, product.stock)
    if new_qty <= 0:
        messages.error(request, "Sorry, that item is out of stock.")
    else:
        cart[str(pk)] = new_qty
        request.session["cart"] = cart
        messages.success(request, f"Added {product.name} to your cart.")
    return redirect(request.POST.get("next") or "cart")


@require_POST
def cart_remove(request, pk):
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    return redirect("cart")


def cart_view(request):
    items, total = _cart_items(request)
    return render(request, "shop/cart.html", {"items": items, "total": total})


@login_required
def checkout(request):
    items, total = _cart_items(request)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("home")
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            locked = {p.pk: p for p in Product.objects.select_for_update().filter(pk__in=[i["product"].pk for i in items])}
            for i in items:
                if locked[i["product"].pk].stock < i["qty"]:
                    messages.error(request, f"Not enough stock for {i['product'].name}.")
                    return redirect("cart")
            order = Order.objects.create(user=request.user, total=total, **form.cleaned_data)
            for i in items:
                p = locked[i["product"].pk]
                OrderItem.objects.create(order=order, product=p, quantity=i["qty"], price=p.price)
                p.stock -= i["qty"]
                p.save(update_fields=["stock"])
        request.session["cart"] = {}
        messages.success(request, f"Order #{order.pk} placed! Pay on delivery.")
        return redirect("orders")
    return render(request, "shop/checkout.html", {"form": form, "items": items, "total": total})


@login_required
def orders(request):
    return render(request, "shop/orders.html", {"orders": request.user.orders.prefetch_related("items__product")})


def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        messages.success(request, "Welcome to Quartico!")
        return redirect("home")
    return render(request, "registration/signup.html", {"form": form})
