from django.conf import settings


def _build_csp(settings) -> str:
    directives = {
        'default-src':  getattr(settings, 'CSP_DEFAULT_SRC',  ("'self'",)),
        'script-src':   getattr(settings, 'CSP_SCRIPT_SRC',   ("'self'",)),
        'style-src':    getattr(settings, 'CSP_STYLE_SRC',    ("'self'",)),
        'font-src':     getattr(settings, 'CSP_FONT_SRC',     ("'self'",)),
        'img-src':      getattr(settings, 'CSP_IMG_SRC',      ("'self'", "data:")),
        'connect-src':  getattr(settings, 'CSP_CONNECT_SRC',  ("'self'",)),
        'frame-src':    getattr(settings, 'CSP_FRAME_SRC',    ("'none'",)),
        'object-src':   getattr(settings, 'CSP_OBJECT_SRC',   ("'none'",)),
        'base-uri':     getattr(settings, 'CSP_BASE_URI',     ("'self'",)),
    }
    return '; '.join(f"{k} {' '.join(v)}" for k, v in directives.items())


_PERMISSIONS_POLICY = (
    'camera=(), microphone=(), geolocation=(), '
    'payment=(), usb=(), magnetometer=(), gyroscope=()'
)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._csp = _build_csp(settings)

    def __call__(self, request):
        response = self.get_response(request)

        if response.get('Content-Disposition', '').startswith('attachment'):
            return response

        response['Content-Security-Policy']         = self._csp
        response['Permissions-Policy']              = _PERMISSIONS_POLICY
        response['Cross-Origin-Opener-Policy']      = 'same-origin'
        response['Cross-Origin-Resource-Policy']    = 'same-origin'
        response['X-Content-Type-Options']          = 'nosniff'

        return response