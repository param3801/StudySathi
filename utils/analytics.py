import time


class Analytics:

    def __init__(self):

        self.history = []

        self.last_update = 0

    def update(self, score):

        now = time.time()

        # Store only once every second
        if now - self.last_update >= 1:

            self.history.append(
                {
                    "time": now,
                    "score": score
                }
            )

            self.last_update = now

    def get_scores(self):

        return [
            item["score"]
            for item in self.history
        ]