import time
import cv2
import mediapipe as mp

from ai.eye import calculate_ear
from ai.alertness import DrowsinessDetector
from ai.blink import BlinkDetector
from ai.yawn import calculate_mar
from ai.yawn_detector import YawnDetector
from ai.head_pose import HeadPoseEstimator
from ai.sleep_tracker import SleepTracker
from ai.score import AlertnessScore
from ai.decision import DecisionEngine
from utils.voice import VoiceAssistant
from utils.state import state
from utils.analytics import Analytics

# Global analytics tracker instance used by line charts
analytics = Analytics()

detector = DrowsinessDetector()
blink_detector = BlinkDetector()
yawn_detector = YawnDetector()
head_pose = HeadPoseEstimator()
sleep_tracker = SleepTracker()
score_engine = AlertnessScore()
decision_engine = DecisionEngine()
voice = VoiceAssistant()

# ⏱ Track time parameters for the 30-second missing face rule
last_face_seen_time = None
voice_cooldown_time = 0  

# Initialize MediaPipe Face Mesh & Hands Solutions
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# 🖐️ Added Visual-Only Hands Tracker Instance
hands_tracker = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ✨ UNIQUE STYLE CONFIG: Ultra-thin, crisp white lines with zero landmark circles
drawing_spec = mp_drawing.DrawingSpec(
    color=(255, 255, 255),
    thickness=1,
    circle_radius=0,
)


def detect_face(frame):
    global last_face_seen_time, voice_cooldown_time

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # ⚡ Run Parallel Model Processing
    face_results = face_mesh.process(rgb)
    hand_results = hands_tracker.process(rgb)
    
    current_time = time.time()
    overlay = frame.copy()

    # 🖐️ Draw Hands Visuals (Independent overlay loop - does not affect face stats)
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                overlay,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec
            )

    # =====================================================
    # CASE 1: NO FACE DETECTED FOR 30 SECONDS TIMEOUT
    # =====================================================
    if not face_results.multi_face_landmarks:
        if last_face_seen_time is None:
            last_face_seen_time = current_time

        elapsed_missing_time = current_time - last_face_seen_time

        if elapsed_missing_time >= 30:
            state.update(
                status="ABSENT",
                score=50,
                recommendation="Left desk unattended. Automated break mode engaged.",
                break_mode=True  
            )
            cv2.putText(
                frame,
                "ABSENT: Break Mode Engaged",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )
        else:
            cv2.putText(
                frame,
                f"No Face! Break in: {int(30 - elapsed_missing_time)}s",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 165, 255),
                2,
            )

        if current_time - voice_cooldown_time > 7:
            voice.speak("No Face Detected!, please come in front of screen.")
            voice_cooldown_time = current_time

        # Blend hand overlays if they exist even when face is missing
        alpha = 1.0
        beta = 0.25
        return cv2.addWeighted(frame, alpha, overlay, beta, 0)

    # =====================================================
    # CASE 2: NORMAL FACE TRACKING MODE
    # =====================================================
    last_face_seen_time = None

    if face_results.multi_face_landmarks:
        count = len(face_results.multi_face_landmarks)
        cv2.putText(
            frame,
            f"Faces: {count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        
        for landmarks in face_results.multi_face_landmarks:
            # Draw face outline contours onto the overlay layer
            mp_drawing.draw_landmarks(
                overlay,
                landmarks,
                mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=drawing_spec,
                connection_drawing_spec=drawing_spec
            )

            h, w, _ = frame.shape

            # Calculate Math Formulations
            ear = calculate_ear(landmarks.landmark, w, h)
            mar = calculate_mar(landmarks.landmark, w, h)
            pitch = head_pose.estimate(landmarks.landmark, w, h)

            status = detector.update(ear)
            sleep_events = sleep_tracker.update(status)
            blink_count = blink_detector.update(ear)
            yawn_count = yawn_detector.update(mar)
            score = score_engine.calculate(blink_count, yawn_count, sleep_events)
            analytics.update(score)

            # Draw Diagnostic HUD Overlay readouts
            cv2.putText(frame, f"EAR: {ear:.2f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"MAR: {mar}", (20, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Yawn Count: {yawn_count}", (20, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Pitch: {pitch:.1f}", (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Sleep Events (60s): {sleep_events}", (20, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(frame, f"Alertness: {score}%", (20, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            decision = decision_engine.decide(score, status, blink_count, yawn_count, sleep_events)

            if decision["level"] in ["HIGH", "MEDIUM"]:
                voice.speak(decision["message"])

            cv2.putText(frame, decision["message"], (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.8, decision["color"], 2)

            # Sync dictionary data out to global reactive Streamlit state core
            state.update(
                status=status,
                score=score,
                blink_count=blink_count,
                yawn_count=yawn_count,
                sleep_events=sleep_events,
                recommendation=decision["message"],
                break_mode=decision["break_mode"]
            )
            
            if status == "FOCUSED":
                color = (0, 255, 0)       
            elif status == "TIRED":
                color = (0, 255, 255)     
            else:
                color = (0, 0, 255)       
          
            cv2.putText(frame, f"Status: {status}", (40, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"Blink Count: {blink_count}", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        # 💫 EXTRA LIGHT BLENDING: Merges both hand skeleton and face lines seamlessly 
        alpha = 1.0
        beta = 0.25  
        frame = cv2.addWeighted(frame, alpha, overlay, beta, 0)

    return frame
