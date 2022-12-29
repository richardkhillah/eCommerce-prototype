from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    if 'admin' in request.path:
        return {}
    
    cart_count = 0
    try:
        cart = Cart.objects.filter(cart_id=_cart_id(request))
        # use the first cart object
        cart_items = CartItem.objects.all().filter(cart=cart[:1])
        for ci in cart_items:
            cart_count += ci.quantity
    except Cart.DoesNotExist or CartItem.DoesNotExist:
        cart_count = 0

    return dict(cart_count=cart_count)