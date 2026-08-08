import time

class BlinkDetector:

    def __init__(self, threshold=0.15):
        self.threshold = threshold
        self.eye_closed = False

        # Store blink timestamps
        self.blinks = []

    def update(self, ear):

        if ear < self.threshold and not self.eye_closed:
            self.eye_closed = True

        elif ear >= self.threshold and self.eye_closed:
            self.eye_closed = False
            self.blinks.append(time.time())

        # Keep only last 60 seconds
        now = time.time()
        self.blinks = [
            t for t in self.blinks
            if now - t <= 60
        ]

        return len(self.blinks)