import logging

_log = logging.getLogger('evently.security')


def log_security_event(
    event: str,
    request=None,
    user=None,
    detail: str = '',
    level: str = 'info',
) -> None:
    """
    Write a structured security event to the security logger.

    Args:
        event:   Short machine-readable event name (e.g. 'login_failure').
        request: Django/DRF request object — used to extract IP and path.
        user:    User object or username string, if known at log time.
        detail:  Free-text additional context.
        level:   'info', 'warning', or 'error'.
    """
    ip   = _get_ip(request)
    path = request.path if request else ''
    ua   = request.headers.get('User-Agent', '')[:200] if request else ''

    uid = None
    uname = None
    if user and hasattr(user, 'pk'):
        uid   = user.pk
        uname = user.username
    elif isinstance(user, str):
        uname = user

    msg = (
        f'[{event}] '
        f'ip={ip} path={path} '
        f'user_id={uid} username={uname} '
        f'detail={detail!r}'
    )

    getattr(_log, level)(msg, extra={
        'security_event': event,
        'ip': ip,
        'path': path,
        'user_agent': ua,
        'user_id': uid,
        'username': uname,
        'detail': detail,
    })


def _get_ip(request) -> str:
    if not request:
        return ''
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')