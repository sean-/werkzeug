# -*- coding: utf-8 -*-
"""
    werkzeug.contrib.limiter
    ~~~~~~~~~~~~~~~~~~~~~~~~

    A middleware that limits incoming data.  This works around problems with
    Trac_ or Django_ because those directly stream into the memory.

    .. _Trac: http://trac.edgewall.org/
    .. _Django: http://www.djangoproject.com/

    :copyright: (c) 2009 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from warnings import warn
from werkzeug.utils import LimitedStream as LimitedStreamBase


class _SilentLimitedStream(LimitedStreamBase):

    def __init__(self, environ, limit):
        LimitedStreamBase.__init__(self,
            environ['wsgi.input'],
            min(limit, int(environ.get('CONTENT_LENGTH') or 0))
        )

    def on_exhausted(self):
        return ''


class LimitedStream(_SilentLimitedStream):

    def __init__(self, environ, limit):
        _SilentLimitedStream.__init__(self, environ, limit)
        warn(DeprecationWarning('comtrin limited stream is deprecated, use '
                                'werkzeug.LimitedStream instead.'),
             stacklevel=2)


class StreamLimitMiddleware(object):
    """Limits the input stream to a given number of bytes.  This is useful if
    you have a WSGI application that reads form data into memory (django for
    example) and you don't want users to harm the server by uploading tons of
    data.

    Default is 10MB
    """

    def __init__(self, app, maximum_size=1024 * 1024 * 10):
        self.app = app
        self.maximum_size = maximum_size

    def __call__(self, environ, start_response):
        environ['wsgi.input'] = _SilentLimitedStream(environ, self.maximum_size)
        return self.app(environ, start_response)
