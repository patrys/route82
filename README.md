route82
=======

A simple URL router for Python

```python
from route82 import Resource, Router, request


def about_view(request):
    return 'About us'


def product_details_view(request, product_id):
    return 'Product: %s' % (product_id,)


router = Router([
    Resource('about', about_view),
    Resource('products', Router([
        Resource(':product_id', product_details_view, name='product-details')]))])

# or shorter:
router = Router([
    ('about', about_view),
    ('products', [
        Resource(':product_id', product_details_view, name='product-details')])])

router.resolve('/about')
# Route(handler=<function about_view ...>, path=u'/about', kwargs={}, parent=Route(handler=<route82.Router object ...>, path=u'', kwargs={}, parent=None))

router.resolve('/products/11')
# Route(handler=<function product_details_view ...>, path=u'/products/11', kwargs={'product_id': u'11'}, parent=Route(handler=<route82.Router object ...>, path=u'/products', kwargs={}, parent=Route(handler=<route82.Router object ...>, path=u'', kwargs={}, parent=None)))

request(router, '/products/25')
# 'Product: 25'
```
