import threading
import time

SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'no-referrer',
    'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'",
}


class LoginThrottle:
    """Limita falhas de login por chave dentro de uma janela de tempo."""

    def __init__(self, max_failures, window_seconds, clock=time.monotonic):
        self._max_failures = max_failures
        self._window_seconds = window_seconds
        self._clock = clock
        self._failures = {}
        self._lock = threading.Lock()

    def _recent(self, key, now):
        return [moment for moment in self._failures.get(key, []) if now - moment < self._window_seconds]

    def is_blocked(self, key):
        with self._lock:
            return len(self._recent(key, self._clock())) >= self._max_failures

    def register_failure(self, key):
        with self._lock:
            now = self._clock()
            recent = self._recent(key, now)
            self._failures = {k: v for k, v in self._failures.items()
                              if v and now - v[-1] < self._window_seconds}
            self._failures[key] = [*recent, now]

    def reset(self, key):
        with self._lock:
            self._failures.pop(key, None)


def register_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response
