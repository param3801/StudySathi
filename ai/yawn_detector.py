import time

class YawnDetector:

    def __init__(self, threshold=0.5, frame_limit=15):

        self.threshold = threshold
        self.frame_limit = frame_limit

        self.open_frames = 0
        self.yawn_active = False

        # Store timestamps
        self.yawns = []

    def update(self, mar):

        if mar > self.threshold:

            self.open_frames += 1

            if (
                self.open_frames >= self.frame_limit
                and not self.yawn_active
            ):
                self.yawns.append(time.time())
                self.yawn_active = True

        else:
            self.open_frames = 0
            self.yawn_active = False

        # Keep only last 60 seconds
        now = time.time()

        self.yawns = [
            t for t in self.yawns
            if now - t <= 60
        ]

        return len(self.yawns)