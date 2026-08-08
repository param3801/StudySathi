from threading import Lock


class AppState:

    def __init__(self):
        self.lock = Lock()

        self.metrics = {
    "status": "Unknown",
    "score": 100,
    "blink_count": 0,
    "yawn_count": 0,
    "sleep_events": 0,
    "recommendation": "Initializing...",
    "break_mode": False
}

    def update(self, **kwargs):
        with self.lock:
            self.metrics.update(kwargs)

    def get(self):
        with self.lock:
            return self.metrics.copy()


state = AppState()