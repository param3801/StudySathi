import pyttsx3
import time


class VoiceAssistant:

    def __init__(self):

        self.engine = None

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 140)

        except Exception:
            # Streamlit Cloud or unsupported environment
            self.engine = None

        # Speak at most once every 30 seconds
        self.cooldown = 30

        self.last_spoken = 0

        # Remember the previous decision
        self.last_message = ""

    def speak(self, message):

        # Voice unavailable (Streamlit Cloud)
        if self.engine is None:
            return

        now = time.time()

        # Don't repeat the same message
        if (
            message == self.last_message
            and message != "No Face Detected!, please come in front of screen."
        ):
            return

        # Respect cooldown
        if now - self.last_spoken < self.cooldown:
            return

        try:
            self.engine.say(message)
            self.engine.runAndWait()

            self.last_spoken = now
            self.last_message = message

        except Exception:
            pass