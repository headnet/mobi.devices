"""
    The TestApp is wrapped into the middleware.

    >>> from playmobile.devices.wsgi.devicedetection\\
    ...   import PlaymobileDeviceMiddleware
    >>> from playmobile.devices.wsgi.devicedetection\\
    ...   import serialize_cookie, deserialize_cookie

    >>> app = TestApp()
    >>> wrapped = PlaymobileDeviceMiddleware(app)

    The environment is set with an user agent string.

    >>> from webob import Request
    >>> request = Request.blank('/')
    >>> request.environ['HTTP_USER_AGENT'] = "Mozilla/5.0 (SymbianOS/9.1;" \\
    ...     " U; [en]; Series60/3.0 NokiaE60/4.06.0) AppleWebKit/413" \\
    ...     " (KHTML, like Gecko) Safari/413"
    >>> request.call_application(wrapped) #doctest: +ELLIPSIS
    ('200 Ok..., ['hello!'])

    Now we can check that the environment contains some info about the device.

    >>> app.environ['playmobile.devices.marker_name']
    'IBasicDeviceType'
    >>> app.environ['playmobile.devices.marker']
    <InterfaceClass playmobile.interfaces.devices.IBasicDeviceType>

    >>> request = Request.blank('/')
    >>> request.environ['HTTP_USER_AGENT'] = "Mozilla/5.0 (iPhone" \\
    ...     " Simulator; U; CPU iPhone OS 3_1_3 like Mac OS X; en-us)" \\
    ...     " AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0" \\
    ...     " Mobile/7E18 Safari/528.16"
    >>> request.call_application(wrapped) #doctest: +ELLIPSIS
    ('200 Ok..., ['hello!'])
    >>> app.environ['playmobile.devices.marker_name']
    'IAdvancedDeviceType'
    >>> app.environ['playmobile.devices.marker']
    <InterfaceClass playmobile.interfaces.devices.IAdvancedDeviceType>

    When the response returns the middle sets a cookie to cache the result
    on the client side.

    >>> request = Request.blank('/')
    >>> response = request.get_response(wrapped)
    >>> response.headers['Set-Cookie'] # doctest: +ELLIPSIS
    '__devinfo=eyJwbGF0Zm9ybSI6ICJmZWF0dXJlcGhvbmUiLCAidHlwZSI6ICJiYXNpYyJ9; Path=/'

    We can set a max-age:
    >>> wrapped.set_cookie_max_age(10000)
    >>> request = Request.blank('/')
    >>> response = request.get_response(wrapped)
    >>> response.headers['Set-Cookie'] # doctest: +ELLIPSIS
    '__devinfo=eyJwbGF0Zm9ybSI6ICJmZWF0dXJlcGhvbmUiLCAidHlwZSI6ICJiYXNpYyJ9; expires="..."; Max-Age=10000; Path=/'

    When client sends a cookie it is used as a cache.

    >>> request = Request.blank('/')
    >>> request.environ['HTTP_COOKIE'] = '__devinfo=%s' % serialize_cookie(
    ...     {'type': 'advanced', 'platform': 'spider'})
    >>> response = request.get_response(wrapped)
    >>> response.headers.get('Set-Cookie', None) is None
    True
    >>> app.environ['playmobile.devices.marker_name']
    'IAdvancedDeviceType'
    >>> app.environ['playmobile.devices.marker']
    <InterfaceClass playmobile.interfaces.devices.IAdvancedDeviceType>
    >>> app.environ['playmobile.devices.platform']
    u'spider'
"""


class TestApp(object):
    """ it only sets the environ attribute. So we can verify some expectations
    on it.
    """
    environ = {}

    def __call__(self, environ, start_response):
        self.environ = environ
        start_response('200 Ok', [('Content-Type', 'text/plain')])
        return ['hello!']

