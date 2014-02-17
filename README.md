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
# Route(handler=<function about_view ...>, path=u'/about', kwargs={},
#   parent=Route(handler=<route82.Router object ...>, path=u'', kwargs={}, parent=None))

request(router, '/products/25')
# 'Product: 25'

router.reverse('product-details', product_id='foo')
# '/products/foo'
```

It supports relative reversing that make namespacing simple:

```python
from route82 import Resource, Router

router = Router([
    (':language', [
        Resource('about', lambda request, language: 'Hello from %s' % (language,)),
        Resource('catalogue', lambda request, language: 'Our products in %s' % (language,),
                 name='catalogue')])])

route = router.resolve('/en-gb/about')
route.reverse('catalogue')
# '/en-gb/catalogue'
route.reverse('catalogue', language='it')
# '/it/catalogue'
```

All wrapped in a nice request object:

```python
from route82 import Resource, Router, request


def simple_view(request):
    return 'This is %s, go see %s' % (
        request.path,
        request.reverse('other-view'))

router = Router([
    ('foo', simple_view),
    Resource('bar', lambda request: 'Woo', name='other-view')])

request(router, '/foo')
# 'This is /foo, go see /bar'
```
