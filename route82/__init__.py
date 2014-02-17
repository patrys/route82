from __future__ import unicode_literals
from collections import namedtuple


class RoutingError(ValueError):
    pass


class ReverseError(ValueError):
    pass


class Request(object):

    def __init__(self, route):
        self.route = route

    @property
    def path(self):
        return self.route.path

    def reverse(self, name, **kwargs):
        return self.route.reverse(name, **kwargs)


def request(router, path, request_class=Request):
    route = router.resolve(path)
    request_object = request_class(route=route)
    return route.handler(request_object, **route.kwargs)


class Route(namedtuple('Route', 'handler, path, kwargs, parent')):
    """
    Represents a resolved path to a view
    """
    def __new__(cls, handler, path, kwargs, parent=None):
        """
        :type kwargs: dict
        :type handler: Router or unknown
        :type parent: Route
        :type path: unicode
        """
        return super(Route, cls).__new__(cls, handler, path, kwargs, parent)

    def root(self):
        if self.parent:
            return self.parent.root()
        return self

    def reverse(self, name, **kwargs):
        if hasattr(self.handler, 'reverse'):
            try:
                return self.handler.reverse(name, prefix=self.path, **kwargs)
            except ReverseError:
                pass
        if self.parent:
            return self.parent.reverse(name, **kwargs)
        raise ReverseError('%r, %r' % (name, kwargs))


class Router(object):
    """
    A collection of resources capable of routing
    """
    def __init__(self, resources):
        """
        :type resources: list of (Resource or tuple)
        """
        self.resources = [
            entry if isinstance(entry, Resource) else Resource(*entry)
            for entry in resources]

    def urls(self, prefix=''):
        for resource in self.resources:
            path = prefix + '/' + resource.resource_name
            if hasattr(resource.handler, 'urls'):
                for sub in resource.handler.urls(path):
                    yield sub
            else:
                yield path, resource.name

    def reverse(self, name, prefix='', **kwargs):
        """
        :type name: unicode
        """
        for resource in self.resources:
            path = prefix + '/' + resource.resource_name
            remaining_kwargs = dict(kwargs)
            for k, v in resource.kwargs.items():
                if not k in remaining_kwargs:
                    continue
                if remaining_kwargs.pop(k) != v:
                    continue
            param = resource.resource_variable
            if param:
                if param in kwargs:
                    resource_value = remaining_kwargs.pop(param)
                    try:
                        resource_name = resource.reverse_resource(
                            resource_value)
                    except (TypeError, ValueError):
                        continue
                    path = prefix + '/' + resource_name
                    if hasattr(resource.handler, 'reverse'):
                        try:
                            return resource.handler.reverse(
                                name, path, **remaining_kwargs)
                        except ReverseError:
                            continue
                    elif resource.name == name and not remaining_kwargs:
                        return path
            elif hasattr(resource.handler, 'reverse'):
                try:
                    return resource.handler.reverse(name, path,
                                                    **remaining_kwargs)
                except ReverseError:
                    continue
            elif resource.name == name and not remaining_kwargs:
                return path
        raise ReverseError('%r, %r' % (name, kwargs))

    def resolve(self, path, prefix='', kwargs=None, parent=None):
        """
        :type path: unicode
        :rtype : Route
        """
        if kwargs is None:
            kwargs = {}
        if path.startswith('/'):
            path = path[1:]
        if '/' in path:
            resource_name, remainder = path.split('/', 1)
        else:
            resource_name, remainder = path, None
        for resource in self.resources:
            if resource.match(resource_name):
                resource_kwargs = dict(kwargs, **resource.kwargs)
                param = resource.resource_variable
                if param:
                    try:
                        resource_kwargs[param] = resource.resolve_resource(
                            resource_name)
                    except (TypeError, ValueError):
                        continue
                resource_path = prefix + '/' + resource_name
                if hasattr(resource.handler, 'resolve'):
                    try:
                        return resource.handler.resolve(
                            remainder, prefix=resource_path,
                            kwargs=resource_kwargs,
                            parent=Route(self, prefix, kwargs, parent=parent))
                    except RoutingError:
                        continue
                elif not remainder:
                    return Route(
                        resource.handler, resource_path, resource_kwargs,
                        parent=Route(self, prefix, kwargs, parent=parent))
        raise RoutingError(path)


class Resource(namedtuple('URL', 'resource_name, handler, name, kwargs')):
    """
    A single named resource
    """
    def __new__(cls, resource_name, handler, name=None, **kwargs):
        """
        :type name: unicode
        :type resource_name: unicode
        """
        if hasattr(handler, '__iter__') and not isinstance(handler, Router):
            handler = Router(handler)
        if '/' in resource_name:
            resource_name, path = resource_name.split('/', 1)
            return cls.__new__(
                cls, resource_name,
                Router([cls.__new__(cls, path, handler, name=name, **kwargs)]))
        return super(Resource, cls).__new__(
            cls, resource_name, handler, name, kwargs)

    def match(self, resource_name):
        """
        :type resource_name: unicode
        """
        return (self.resource_name == resource_name or
                self.resource_name.startswith(':'))

    @property
    def resource_variable(self):
        if self.resource_name.startswith(':'):
            return self.resource_name[1:]

    def reverse_resource(self, resource_value):
        return str(resource_value)

    def resolve_resource(self, resource_name):
        return resource_name
