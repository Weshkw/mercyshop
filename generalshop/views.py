import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import cart as shopping_cart
from .forms import FeaturedVideoForm, PettyCostsForm, ProductForm
from .models import FeaturedVideo, InventoryProducts, OtherPettyCosts, PettyCosts


def home(request):
    search_term = request.GET.get("q", "").strip()
    products = InventoryProducts.objects.all()
    if search_term:
        products = products.filter(
            Q(product_name__icontains=search_term) | Q(description__icontains=search_term)
        )
    context = {
        "products": products,
        "search_term": search_term,
        "videos": FeaturedVideo.objects.all()[:3],
    }
    return render(request, "generalshop/home.html", context)


def product_detail(request, pk):
    product = get_object_or_404(InventoryProducts.objects.prefetch_related("moreimages"), pk=pk)
    return render(request, "generalshop/product_detail.html", {"product": product})


def cart(request):
    return render(request, "generalshop/cart.html", {"cart": shopping_cart.get_cart(request)})


@require_POST
def update_cart(request):
    """Apply one cart action sent as JSON: {"product_id": 1, "action": "add"}."""
    try:
        payload = json.loads(request.body)
        action = shopping_cart.CART_ACTIONS[payload["action"]]
        product = InventoryProducts.objects.get(pk=int(payload["product_id"]))
    except (ValueError, KeyError, TypeError, InventoryProducts.DoesNotExist):
        return JsonResponse({"error": "Unknown product or action."}, status=400)

    action(shopping_cart.get_or_create_cart(request), product)

    cart = shopping_cart.get_cart(request)
    line = next((line for line in cart.ordered_products.all() if line.product == product), None)
    return JsonResponse(
        {
            "quantity": line.quantity if line else 0,
            "line_total": str(line.line_total) if line else "0.00",
            "cart_total": str(cart.total),
            "cart_count": cart.item_count,
        }
    )


@login_required
@permission_required("generalshop.add_inventoryproducts", raise_exception=True)
def create_product(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"{product.product_name} was added to the shop.")
        return redirect("product-detail", pk=product.pk)
    return render(request, "generalshop/create_product.html", {"form": form})


@login_required
@permission_required("generalshop.add_featuredvideo", raise_exception=True)
def add_video(request):
    form = FeaturedVideoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "The video is now featured on the home page.")
        return redirect("home")
    return render(request, "generalshop/add_video.html", {"form": form})


@login_required
def petty_costs(request):
    form = PettyCostsForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save_for(request.user)
        messages.success(request, "Expense recorded.")
        return redirect("petty-costs")

    entries = PettyCosts.objects.filter(employee=request.user).prefetch_related("other_costs")
    totals = entries.aggregate(
        transport=Sum("transport_cost"), lunch=Sum("lunch_cost"), airtime=Sum("airtime_cost")
    )
    totals["other"] = OtherPettyCosts.objects.filter(pettycosts__employee=request.user).aggregate(
        total=Sum("expense")
    )["total"]
    context = {"form": form, "entries": entries, "totals": totals}
    return render(request, "generalshop/petty_costs.html", context)
