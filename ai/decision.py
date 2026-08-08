from utils.state import state
class DecisionEngine:

    def __init__(self):
        self.break_shown = False

    def decide(self, score, status, blink_rate, yawn_rate, sleepy_events):

        break_mode = state.metrics["break_mode"]
        
        if score <= 50 or sleepy_events >= 2:

            if not self.break_shown :
                break_mode = True
                self.break_shown = True

        else:
            # break_mode = False
            self.break_shown = False

        # Existing decision logic
        if score <= 40:
            level = "HIGH"
            message = "You seem very tired. Take a 5-minute break."
            color = (0, 0, 255)

        elif score <= 70:
            level = "MEDIUM"
            message = "Stay alert. Drink some water or stretch."
            color = (0, 255, 255)

        else:
            level = "LOW"
            message = "Great! Keep studying."
            color = (0, 255, 0)

        return {
            "level": level,
            "message": message,
            "color": color,
            "break_mode": break_mode
        }