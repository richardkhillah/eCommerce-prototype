from django.shortcuts import render, get_object_or_404

from cart.models import CartItem
from category.models import Category

from .models import Product
from cart.views import _cart_id

# Create your views here.
def store(request, category_slug=None):
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.all().filter(is_available=True)
    
    context = {
        'products': products,
    }
    return render(request, 'store.html', context=context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'product_detail.html', context=context)