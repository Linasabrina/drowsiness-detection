import speech_recognition as sr
import time

print("\n🎤 TEST SEMUA MIKROFON\n")

recognizer = sr.Recognizer()
mic_list = sr.Microphone.list_microphone_names()

# Filter cuma yang "Input" atau "Microphone"
input_mics = []
for i, name in enumerate(mic_list):
    if "input" in name.lower() or "microphone" in name.lower() or "mic" in name.lower():
        input_mics.append((i, name))

print(f"Ditemukan {len(input_mics)} mikrofon input:\n")

for mic_idx, mic_name in input_mics:
    print("="*60)
    print(f"[{mic_idx}] {mic_name}")
    print("="*60)
    
    try:
        with sr.Microphone(device_index=mic_idx) as source:
            # Kalibrasi cepat
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = False
            
            print("🗣️ Bicara 'testing' SEKARANG! (5 detik)")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            print("🔄 Memproses...")
            result = recognizer.recognize_google(audio, language="id-ID")
            print(f"✅ BERHASIL: '{result}'\n")
            print(f"🎯 MIKROFON INI BAGUS! Gunakan index: {mic_idx}\n")
            break  # Stop kalau udah ketemu yang bagus
            
    except sr.WaitTimeoutError:
        print("⏰ Timeout\n")
    except sr.UnknownValueError:
        print("⚠️ Tidak jelas (volume terlalu kecil)\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    time.sleep(1)

print("="*60)
print("✅ Test selesai")