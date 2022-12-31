from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponse

from store.models import Product, Variation

from .models import Cart, CartItem

# Create your views here.

def _cart_id(request):
    # Use the session id as cart id.
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_item(request, product_id):
    """Increment cart item by one"""
    # Get the product variations from Post request
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for key, value in request.POST.items():
            try:
                # Filter out only the relevant information 
                variation = Variation.objects.get(product=product, 
                                                variation_category__iexact=key, 
                                                variation_value__iexact=value)
                # add the product variation
                product_variation.append(variation)
            except:
                # Not a varient
                pass
    
    # Add the product to the cart
    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
    cart_items = CartItem.objects.filter(product=product, cart=cart)

    # If the variation already exists in the cart, increment the quantity
    added = False
    for ci in cart_items:
        if product_variation == list(ci.variations.all()):
            ci.quantity += 1
            added = True
            ci.save()
            break
    
    # Otherwise, create a new item
    if not added:
        ci = CartItem.objects.create(product=product, cart=cart, quantity=1)
        ci.variations.add(*product_variation)
        ci.save()
    
    return redirect('cart')

def remove_item(request, product_id, cart_item_id):
    """Decerement cart item by one"""
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
    try:
        # Decrement or remove the item varient from the cart
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    """Remove all items of the varient from the cart"""
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    try:
        cart_item = CartItem.objects.filter(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except:
        pass
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = 0.095 * total
        grand_total = total + tax
    except ObjectDoesNotExist:
        #TODO: Fix this Make handling better
        tax=0
        grand_total=0

    context = {
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'quantity': quantity,
        'cart_items': cart_items,
    }

    return render(request, 'cart.html', context=context)