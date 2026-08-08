class DrowsinessDetector:
    def __init__(self):
        self.closed_frames = 0

        self.sleep_threshold = 0.17
        self.tired_threshold = 0.20

        self.frame_limit = 60      # 2 seconds at ~30 FPS

    def update(self, ear):

        # Sleep detection
        if ear < self.sleep_threshold:
            self.closed_frames += 1
        else:
            self.closed_frames = 0

        # If eyes closed for 2 seconds
        if self.closed_frames >= self.frame_limit:
            return "SLEEPY"

        # Eye partially closed
        elif ear < self.tired_threshold:
            return "TIRED"

        # Eye open
        else:
            return "FOCUSED"