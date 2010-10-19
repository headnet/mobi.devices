# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt.
from webob import Request
import logging
from mobi.devices.index.radixtree import RadixTree, WildcardSearch


logger = logging.getLogger('mobi.devices.wsgi.router')

mobile_matches = ['android',
                  'symbianos'
                  'iphone',
                  'windows ce',
                  'opera mini',
                  'opera mobi',
                  'nokia'
                  'blackberry'
                  'nokia'
                  'motorola',
                  'ericsson']


class RouterMiddleware(object):
    """ Middleware to redirect mobile devices to mobile sites

    RouterMiddleWare(app, config_map)

    config_map is a dict where keys are computer site hostnames and values
    mobile site hostnames or urls.
    """
    no_redirect_param_name = '__no_redirect'

    def __init__(self, app, config_map):
        self.app = app
        self._config = self._parse_config(config_map)
        self._init_search()
        logger.info("mobi.devices router config :\n %s" %
                    str(self._config))

    def _init_search(self):
        tree = RadixTree()
        for name in mobile_matches:
            self._search_trie.add(name)
        self._search = WildcardSearch(tree)

    def _parse_config(self, config_map):
        config = {}
        for normal_host, mobile_host in config_map.iteritems():
            if mobile_host.startswith('http://')\
                    or mobile_host.startswith('https://'):
                config[normal_host] = mobile_host
            else:
                config[normal_host] = "http://%s/" % mobile_host
        return config

    def is_mobile(self, request):
        # Check for WAP Profile header, if there is one then this is a mobile
        wap_profile = request.environ.get('HTTP_X_WAP_PROFILE', None)
        if wap_profile is not None:
            return True

        user_agent = request.environ.get('HTTP_USER_AGENT', None)
        if user_agent is not None:
            results = self._search(user_agent.lower())
            if len(results) > 0:
                return True
        return False

    def __call__(self, environ, start_response):
        port = 80
        hostname = environ.get('HTTP_HOST', '')
        if ":" in hostname:
            hostname, port = hostname.split(':', 1)

        # nothing configure for this host bail out
        if hostname not in self._config:
            return self.app(environ, start_response)

        request = Request(environ)
        no_redirect_param = request.GET.get(self.no_redirect_param_name)
        no_redirect_cookie = request.cookies.get(self.no_redirect_param_name)

        force_no_redirect = no_redirect_param or no_redirect_cookie

        # mobi.devices middleware has tagged it as mobile
        if self.is_mobile(request):
            if force_no_redirect:
                response = request.get_response(self.app)
                if not no_redirect_cookie:
                    response.set_cookie(
                        self.no_redirect_param_name, 'on', path="/")
                return response(environ, start_response)

            target = self._config[hostname]
            start_response('302 Redirect', [('Location', target,)])
            return []

        return self.app(environ, start_response)


# paste deploy entry point
def router_middleware_filter_factory(global_conf, **local_conf):
    def filter(app):
        return RouterMiddleware(app, local_conf)

    return filter
