from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from cart.models import CartItem
from category.models import Category

from .models import Product
from cart.views import _cart_id

# Create your views here.
def store(request, category_slug=None):
    
    def paginate(items, per_page=3):
        paginator = Paginator(items, per_page)
        page = request.GET.get('page')
        paginated_items = paginator.get_page(page)
        return paginated_items

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        items = Product.objects.filter(category=categories, is_available=True).order_by('product_name')
        paginated_products = paginate(items)
    else:
        products = Product.objects.all().filter(is_available=True).order_by('product_name')
        paginated_products = paginate(products)
    
    context = {
        'products': paginated_products,
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

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)).order_by('-created_date')
        else:
            products = []
        context = {
            'products': products
        }
    return render(request, 'store.html', context=context)