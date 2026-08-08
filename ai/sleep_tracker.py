import time


class SleepTracker:

    def __init__(self):

        self.events = []
        self.was_sleepy = False

    def update(self, status):

        if status == "SLEEPY":

            if not self.was_sleepy:
                self.events.append(time.time())
                self.was_sleepy = True

        else:
            self.was_sleepy = False

        now = time.time()

        self.events = [
            t for t in self.events
            if now - t <= 60
        ]

        return len(self.events)