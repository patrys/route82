from __future__ import print_function, unicode_literals
from unittest import TestCase

from . import Resource, ReverseError, Router


class RouteTest(TestCase):

    def test_reverse_works_with_partial_variables(self):
        router = Router([
            (':foo', [
                ('first', lambda request: None),
                ('second', lambda request: None, 'bar')])])
        route = router.resolve('/123/first')
        self.assertEqual(route.reverse('bar'), '/123/second')

    def test_reverse_works_with_full_variables(self):
        router = Router([
            (':foo', [
                ('first', lambda request: None),
                ('second', lambda request: None, 'bar')])])
        route = router.resolve('/123/first')
        self.assertEqual(route.reverse('bar', foo='456'), '/456/second')

    def test_reverse_returns_closest_match(self):
        router = Router([
            ('foo', lambda request: request.reverse('foo'), 'foo'),
            ('bar', [
                ('baz', lambda request: None, 'foo'),
                ('42', lambda request: request.reverse('foo'))])])
        route = router.resolve('/foo')
        self.assertEqual(route.reverse('foo'), '/foo')
        route = router.resolve('/bar/42')
        self.assertEqual(route.reverse('foo'), '/bar/baz')


class RouterTest(TestCase):

    def test_variable_based_routing(self):
        router = Router([
            (':foo/:bar', lambda request: None)])
        route = router.resolve('/11/12')
        self.assertEqual(route.path, '/11/12')
        self.assertEqual(route.kwargs, {'foo': '11', 'bar': '12'})

    def test_prepared_resource(self):
        router = Router([
            (':res_name', lambda request, res_name: None)])
        route = router.resolve('/aa/')
        self.assertEqual(route.kwargs, {'res_name': 'aa'})

    def test_simple_reverse(self):
        router = Router([('foo', lambda request: None, 'bar')])
        self.assertEqual(router.reverse('bar'), '/foo')

    def test_variable_based_reverse(self):
        router = Router([
            (':foo', lambda request: None, 'bar')])
        self.assertRaises(ReverseError,
                          lambda: router.reverse('bar'))
        self.assertEqual(router.reverse('bar', foo='baz'), '/baz')

    def test_reverse_fails_with_unmatched_arguments(self):
        router = Router([
            ('foo', lambda request: None, 'bar')])
        self.assertRaises(ReverseError,
                          lambda: router.reverse('bar', extra='baz'))

    def test_reverse_supports_multiple_variables(self):
        router = Router([
            (':foo', [
                (':bar', lambda request: None, 'bar')])])
        self.assertRaises(ReverseError,
                          lambda: router.reverse('bar', foo='baz'))
        self.assertEqual(router.reverse('bar', foo='baz1', bar='baz2'),
                         '/baz1/baz2')

    def test_reverse_handles_multiple_paths(self):
        router = Router([
            (':foo/first', lambda request: None),
            (':foo/second', lambda request: None, 'bar')])
        self.assertEqual(router.reverse('bar', foo='baz'), '/baz/second')

    def test_reverse_returns_first_match(self):
        router = Router([
            ('baz/first', lambda request: None, 'bar'),
            ('baz/second', lambda request: None, 'bar')])
        self.assertEqual(router.reverse('bar'), '/baz/first')

    def test_resolve(self):
        def stub():
            pass

        router = Router([
            ('baz/first', stub, 'bar'),
            ('baz/second', lambda request: None, 'bar')])
        route = router.resolve('/baz/first')
        self.assertEqual(route.path, '/baz/first')
        self.assertEqual(route.handler, stub)
        self.assertEqual(route.kwargs, {})

    def test_resolve_works_on_resources_with_kwargs(self):
        router = Router([
            Resource('foo/bar', lambda request: None, baz=11)])
        route = router.resolve('/foo/bar')
        self.assertEqual(route.kwargs, {'baz': 11})

    def test_reverse_works_on_resources_with_kwargs(self):
        router = Router([
            Resource('foo/bar', lambda request: None, 'bar', baz=11)])
        self.assertEqual(router.reverse('bar', baz=11), '/foo/bar')
