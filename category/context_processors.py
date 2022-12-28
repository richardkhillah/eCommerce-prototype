"""Take a request as arguement and return a dictionary of data
    as a context.

    This allows global use.

    each context processor below must be registered in settings
"""

from .models import Category

def menu_links(request):
    """Query all category objects and send to context"""
    links = Category.objects.all()
    return dict(links=links)