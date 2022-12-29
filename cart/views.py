from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponse

from store.models import Product

from .models import Cart, CartItem

# Create your views here.

def _cart_id(request):
    # Use the session id as cart id.
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_item(request, product_id):
    product = Product.objects.get(id=product_id)

    # Get the cart to add the product to
    try:
        # Use the cart/session id to get the cart
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    
    # Add the product to the cart
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        # cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product, 
            cart=cart,
            quantity=1
        )
    finally:
        cart_item.save()
    return redirect('cart')

def remove_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
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
    except Cart.ObjectNotExist:
        pass
    context = {
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'quantity': quantity,
        'cart_items': cart_items,
    }

    return render(request, 'cart.html', context=context)