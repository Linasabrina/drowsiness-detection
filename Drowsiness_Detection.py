import cv2
import imutils
from imutils import face_utils
import dlib
from scipy.spatial import distance
from gtts import gTTS
import speech_recognition as sr
import threading
import subprocess
import pygame
import tempfile
import os
import time
import sys
import uuid
import glob
import random
import mediapipe as mp

# --- Inisialisasi pygame & mediapipe ---
pygame.mixer.init()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# --- Fungsi deteksi mata & mulut ---
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def mouth_aspect_ratio(mouth):
    A = distance.euclidean(mouth[13], mouth[19])
    B = distance.euclidean(mouth[14], mouth[18])
    C = distance.euclidean(mouth[15], mouth[17])
    D = distance.euclidean(mouth[12], mouth[16])
    return (A + B + C) / (3.0 * D)

# --- Fungsi deteksi gesture tangan ---
def detect_hand_gesture(hand_landmarks):
    """
    Deteksi gesture:
    - 'open' = telapak terbuka (semua jari terentang)
    - 'fist' = kepalan (semua jari tertutup)
    - None = gesture tidak dikenali
    """
    if not hand_landmarks:
        return None
    
    landmarks = hand_landmarks.landmark
    
    # Indeks landmark: thumb=4, index=8, middle=12, ring=16, pinky=20
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Base/MCP joints
    thumb_mcp = landmarks[2]
    index_mcp = landmarks[5]
    middle_mcp = landmarks[9]
    ring_mcp = landmarks[13]
    pinky_mcp = landmarks[17]
    
    # Hitung jari yang terentang
    fingers_extended = 0
    
    # Index finger
    if index_tip.y < index_mcp.y:
        fingers_extended += 1
    
    # Middle finger
    if middle_tip.y < middle_mcp.y:
        fingers_extended += 1
    
    # Ring finger
    if ring_tip.y < ring_mcp.y:
        fingers_extended += 1
    
    # Pinky
    if pinky_tip.y < pinky_mcp.y:
        fingers_extended += 1
    
    # Thumb (horizontal check)
    if abs(thumb_tip.x - thumb_mcp.x) > 0.1:
        fingers_extended += 1
    
    # Deteksi gesture
    if fingers_extended >= 4:
        return 'open'  # Telapak terbuka
    elif fingers_extended <= 1:
        return 'fist'  # Kepalan
    else:
        return None

# --- Fungsi TTS Indonesia (gTTS + pygame) FIXED ---
def speak(text, wait=False):
    def run():
        temp_path = None
        try:
            pygame.mixer.music.stop()
            
            # Gunakan prefix konsisten untuk filtering nanti
            temp_filename = f"tts_temp_{uuid.uuid4().hex}.mp3"
            temp_path = os.path.join(tempfile.gettempdir(), temp_filename)

            tts = gTTS(text=text, lang='id')
            tts.save(temp_path)

            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            pygame.mixer.music.unload()
            time.sleep(0.3)
            
            for attempt in range(5):
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    break
                except PermissionError:
                    if attempt < 4:
                        time.sleep(0.5)
                    else:
                        print(f"⚠️ Gagal hapus file: {temp_path}")
                        
        except Exception as e:
            print(f"TTS Error: {e}")
            if temp_path and os.path.exists(temp_path):
                try:
                    pygame.mixer.music.unload()
                    time.sleep(0.2)
                    os.remove(temp_path)
                except:
                    pass

    if wait:
        run()
    else:
        threading.Thread(target=run, daemon=True).start()

# --- Fungsi dengar suara FIXED ---
def listen():
    recognizer = sr.Recognizer()
    
    with sr.Microphone(device_index=1) as source:
        print("🎧 Mendengarkan jawaban...")
        
        # Set threshold FIXED 200 (hasil test)
        recognizer.energy_threshold = 150
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.6
        
        print(f"   ⚙️ Threshold: {recognizer.energy_threshold}")
        
        try:
            print("🗣️ Silakan bicara...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=7)
            
            print("🔄 Memproses suara...")
            response = recognizer.recognize_google(audio, language="id-ID")
            print(f"✅ Kamu berkata: '{response}'")
            return response.lower()
            
        except sr.WaitTimeoutError:
            print("⏰ Tidak ada suara terdeteksi dalam 10 detik.")
            return ""
        except sr.UnknownValueError:
            print("⚠️ Suara tidak jelas, coba ulangi.")
            return ""
        except sr.RequestError as e:
            print(f"❌ Error Google API: {e}")
            return ""
        except Exception as e:
            print(f"🎤 Error: {e}")
            return ""

# --- Fungsi putar alarm untuk drowsiness ---
def play_alarm():
    """Play alarm sound untuk drowsiness detection"""
    alarm_file = "C:/Drowsiness_Detection/Digital alarm clock sound effect beeping sounds.mp3"
    
    if not os.path.exists(alarm_file):
        print("⚠️ File alarm tidak ditemukan!")
        return
    
    try:
        # Load alarm sebagai Sound object (channel terpisah dari musik)
        alarm_sound = pygame.mixer.Sound(alarm_file)
        alarm_sound.set_volume(0.7)
        alarm_sound.play()
        
        # Tunggu alarm selesai (max 3 detik)
        time.sleep(min(alarm_sound.get_length(), 3.0))
        
    except Exception as e:
        print(f"❌ Error play alarm: {e}")

# --- Fungsi putar musik dari file lokal (random) ---
def play_music():
    def play_in_background():
        music_folder = "C:/Drowsiness_Detection/music/"
        music_files = glob.glob(os.path.join(music_folder, "*.mp3"))
        
        # Filter: exclude voice_*.mp3 dan alarm file
        excluded = ["voice_", "Digital alarm clock", "alarm"]
        music_files = [f for f in music_files 
                      if not any(ex in os.path.basename(f) for ex in excluded)]
        
        if not music_files:
            print("❌ Tidak ada file musik (.mp3) di folder")
            speak("Maaf, tidak ada file musik tersedia.", wait=False)
            return
        
        music_file = random.choice(music_files)
        
        try:
            print(f"🎶 Memutar: {os.path.basename(music_file)}")
            
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play()
            
            print("✅ Musik sedang diputar")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    threading.Thread(target=play_in_background, daemon=True).start()

# --- Parameter deteksi ---
EYE_THRESH = 0.25
MOUTH_THRESH = 0.3
FRAME_CHECK = 25

yawn_frames = 0
YAWN_FRAME_CHECK = 10
YAWN_COOLDOWN = 100
yawn_cooldown_counter = 0

# Gesture detection state
gesture_frames = 0
GESTURE_FRAME_CHECK = 15  # Butuh 15 frame konsisten (~0.5 detik)
last_gesture = None
gesture_cooldown = 0
GESTURE_COOLDOWN = 60  # Cooldown 60 frame (~2 detik) setelah gesture

# Drowsiness cooldown (hindari trigger berulang)
drowsy_cooldown = 0
DROWSY_COOLDOWN = 150  # 5 detik cooldown setelah alarm

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
cap = cv2.VideoCapture(0)

sleep_frames = 0
yawn_detected = False
frame_brightness = 1.0  # Brightness multiplier (0.5 - 2.0)

print("\n🚀 Sistem Drowsiness Detection!")
print("\n🤚 Kontrol Gesture (Saat Musik Jalan):")
print("   ✋ Telapak terbuka = Ganti lagu")
print("   ✊ Kepalan = Stop musik")
print("\n⌨️  Kontrol Keyboard:")
print("   [ = Turunkan brightness")
print("   ] = Naikkan brightness")
print("   Q = Quit\n")

# --- Loop utama ---
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = imutils.resize(frame, width=450)
    
    # Apply brightness adjustment
    if frame_brightness != 1.0:
        frame = cv2.convertScaleAbs(frame, alpha=frame_brightness, beta=0)
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    subjects = detect(gray, 0)
    
    # Deteksi tangan dengan MediaPipe
    hand_results = hands.process(frame_rgb)
    current_gesture = None
    
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            # Gambar skeleton tangan
            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx = connection[0]
                end_idx = connection[1]
                start = hand_landmarks.landmark[start_idx]
                end = hand_landmarks.landmark[end_idx]
                h, w, _ = frame.shape
                start_point = (int(start.x * w), int(start.y * h))
                end_point = (int(end.x * w), int(end.y * h))
                cv2.line(frame, start_point, end_point, (0, 255, 255), 2)
            
            current_gesture = detect_hand_gesture(hand_landmarks)
    
    # Update gesture cooldown
    if gesture_cooldown > 0:
        gesture_cooldown -= 1
    
    # Proses gesture HANYA jika musik sedang jalan
    if pygame.mixer.music.get_busy() and current_gesture and gesture_cooldown == 0:
        if current_gesture == last_gesture:
            gesture_frames += 1
            
            if gesture_frames >= GESTURE_FRAME_CHECK:
                if current_gesture == 'open':
                    print("🔄 Ganti lagu via gesture")
                    pygame.mixer.music.stop()
                    time.sleep(0.3)
                    play_music()
                    gesture_frames = 0
                    gesture_cooldown = GESTURE_COOLDOWN
                    
                elif current_gesture == 'fist':
                    print("⏹️ Stop musik via gesture")
                    pygame.mixer.music.stop()
                    gesture_frames = 0
                    gesture_cooldown = GESTURE_COOLDOWN
        else:
            gesture_frames = 0
            last_gesture = current_gesture
    else:
        if not pygame.mixer.music.get_busy():
            gesture_frames = 0
        last_gesture = current_gesture
    
    # Tampilkan gesture detection status HANYA saat musik jalan
    if pygame.mixer.music.get_busy() and current_gesture and gesture_cooldown == 0:
        gesture_text = "✋ OPEN" if current_gesture == 'open' else "✊ FIST"
        progress = min(gesture_frames / GESTURE_FRAME_CHECK, 1.0)
        color = (0, 255, 0) if progress >= 1.0 else (255, 165, 0)
        cv2.putText(frame, f"{gesture_text} {int(progress*100)}%", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Tampilkan status musik
    if pygame.mixer.music.get_busy():
        cv2.putText(frame, "Music Playing", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    if len(subjects) > 0:
    # Pilih wajah dengan bounding box terbesar
        subject = max(subjects, key=lambda r: r.width() * r.height())
    
        shape = predict(gray, subject)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        ear = (eye_aspect_ratio(leftEye) + eye_aspect_ratio(rightEye)) / 2.0

        mouth = shape[mStart:mEnd]
        mar = mouth_aspect_ratio(mouth)

        cv2.drawContours(frame, [cv2.convexHull(leftEye)], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [cv2.convexHull(rightEye)], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [cv2.convexHull(mouth)], -1, (255, 0, 0), 1)

        # --- Deteksi kantuk ---
        if ear < EYE_THRESH:
            sleep_frames += 1
            if sleep_frames >= FRAME_CHECK:
                cv2.putText(frame, "Drowsy...", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                print("🚨 DROWSINESS DETECTED!")
                play_alarm()
                
                speak("Kamu terlihat mengantuk, ayo istirahat sebentar.", wait=False)
                # Set cooldown
                drowsy_cooldown = DROWSY_COOLDOWN
                sleep_frames = 0
        else:
            sleep_frames = 0

        if yawn_cooldown_counter > 0:
            yawn_cooldown_counter -= 1
            cv2.putText(frame, f"Cooldown: {yawn_cooldown_counter}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 1)
        
        if mar > MOUTH_THRESH and yawn_cooldown_counter == 0:
            yawn_frames += 1
            if yawn_frames >= YAWN_FRAME_CHECK and not yawn_detected:
                yawn_detected = True
                yawn_cooldown_counter = YAWN_COOLDOWN
                
                cv2.putText(frame, "Yawning...", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                def ask_music():
                    global yawn_detected
                    
                    print("\n" + "="*50)
                    print("🥱 MENGUAP TERDETEKSI")
                    print("="*50)
                    
                    speak("Kamu menguap! Minumlah air putih atau mau aku putarkan musik?", wait=True)
                    time.sleep(1.5)
                    
                    response = listen()
                    print(f"📝 Response: '{response}'")
                    
                    positive = ["ya", "iya", "ia", "yah", "boleh", "putar", "oke", "ok", "musik", "mau", "tolong", "sip"]
                    negative = ["tidak", "nggak", "ga", "enggak", "jangan", "gausah"]
                    
                    if any(word in response for word in negative):
                        speak("Baik, istirahat dulu ya.", wait=False)
                        print("❌ User menolak")
                    elif any(word in response for word in positive):
                        speak("Oke.", wait=False)
                        time.sleep(1)
                        play_music()
                        print("✅ Musik diputar! Gesture control aktif")
                    elif response == "":
                        speak("Sepertinya kamu tidak menjawab, istirahat dulu ya.", wait=False)
                        print("⚠️ Timeout")
                    else:
                        speak("Maaf, aku tidak mengerti. Istirahat dulu ya.", wait=False)
                        print(f"❓ Tidak dikenali: '{response}'")
                    
                    yawn_detected = False
                    print("="*50 + "\n")

                threading.Thread(target=ask_music, daemon=True).start()
        else:
            yawn_frames = 0

    # Tampilkan brightness level
    cv2.putText(frame, f"Brightness: {int(frame_brightness*100)}%", (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Drowsiness & Yawn Detection", frame)

    # Keyboard controls
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('['):  
        frame_brightness = max(0.3, frame_brightness - 0.1)
        print(f"🔅 Brightness: {int(frame_brightness*100)}%")
    elif key == ord(']'):  
        frame_brightness = min(2.0, frame_brightness + 0.1)
        print(f"🔆 Brightness: {int(frame_brightness*100)}%")

cap.release()
cv2.destroyAllWindows()
hands.close()
pygame.mixer.quit()
print("\n👋 Program selesai. Terima kasih!")