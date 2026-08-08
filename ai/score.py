import time
class AlertnessScore:

    def calculate(
        self,
        blink_rate,
        yawn_rate,
        sleepy_events
        
    ):

        score = 100
        

        # Sleep events have the highest impact
        score -= sleepy_events * 20

        # Each yawn reduces the score
        score -= yawn_rate * 8

        # Blink rate assessment
        if blink_rate < 8:
            score -= 5
        elif blink_rate > 25:
            score -= 10

        return max(0, min(score, 100))