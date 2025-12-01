# Driver Drowsiness Detection System with Gesture Control

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange.svg)

Sebuah sistem computer vision real-time yang dirancang untuk mendeteksi tanda-tanda kantuk pada pengemudi (mata terpejam dan menguap) dan memberikan peringatan dini.

Sistem ini tidak hanya membunyikan alarm, tetapi juga berinteraksi dengan pengguna melalui suara dan memungkinkan kontrol musik menggunakan gestur tangan tanpa sentuhan agar pengemudi tetap terjaga.

---

## Fitur Utama

* **Deteksi Kantuk (Mata):** Menggunakan *Eye Aspect Ratio* (EAR) dengan dlib 68 face landmarks untuk mendeteksi jika mata terpejam terlalu lama.
* **Deteksi Menguap (Mulut):** Menggunakan *Mouth Aspect Ratio* (MAR) untuk mendeteksi aktivitas menguap.
* **Alarm Peringatan:** Memutar suara alarm keras jika terdeteksi sangat mengantuk.
* **Interaksi Suara (Voice Assistant):**
    * Sistem akan menyapa saat pengguna terdeteksi menguap.
    * Menawarkan untuk memutar musik via *Text-to-Speech* (gTTS) Bahasa Indonesia.
    * Mendengarkan jawaban "Ya" atau "Tidak" via *Speech Recognition*.
* **Kontrol Musik via Gestur Tangan (MediaPipe):**
    * **Telapak Terbuka (Open Palm):** Ganti ke lagu berikutnya secara acak.
    * **Kepalan Tangan (Fist):** Hentikan musik.
* **Kontrol Kecerahan:** Penyesuaian kecerahan frame kamera menggunakan keyboard untuk kondisi minim cahaya.

---

## Prasyarat (Dependencies)

Proyek ini dikembangkan menggunakan Python. Pustaka utama yang digunakan:

* OpenCV (`opencv-python`)
* dlib
* MediaPipe (`mediapipe`)
* imutils
* pygame (untuk audio)
* gTTS (Google Text-to-Speech)
* SpeechRecognition & PyAudio (untuk input mikrofon)
* SciPy

### Catatan Instalasi Penting (Windows)
Instalasi `dlib` dan `PyAudio` terkadang memerlukan langkah ekstra di Windows jika `pip install` biasa gagal:

1.  **dlib:** Pastikan kamu sudah menginstal CMake dan Visual Studio Build Tools dengan "Desktop development with C++".
2.  **PyAudio:** Jika gagal, download file `.whl` yang sesuai dengan versi Pythonmu dari [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio), lalu install via pip: `pip install nama_file.whl`.

---

## Cara Instalasi dan Menjalankan

Ikuti langkah-langkah ini untuk menjalankan proyek di komputer lokalmu:

### 1. Clone Repository
```bash
git clone [https://github.com/Linasabrina/drowsiness-detection.git](https://github.com/Linasabrina/drowsiness-detection.git)
cd drowsiness-detection
```

### 2. Siapkan Virtual Environment (Opsional tapi Disarankan)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install opencv-python dlib imutils scipy gTTS SpeechRecognition pygame mediapipe pyaudio
```

### 4. Siapkan File Pendukung
Agar program berjalan, kamu harus menyiapkan struktur folder dan file berikut di dalam folder proyek:
* **Root Folder Proyek**
    * main_script.py (File kode Python utamamu)
    * shape_predictor_68_face_landmarks.dat (Download dari [sini](https://drive.google.com/drive/folders/1uMQpBDky9NCcCgfmOpDiQr5p-xttdvPU) dan ekstrak)
    * music (Buat folder baru bernama music)
       * Masukkan file lagu-lagu .mp3 favoritmu di sini.

### 5. Jalankan Program
```bash
python main_script.py
```

---

## Kontrol Penggunaan

Saat program berjalan:

**Gestur Tangan** (Hanya aktif saat musik diputar)
Arahkan tangan ke kamera:
* Telapak Terbuka: Ganti lagu (Next shuffle).
* Kepalan Tangan: Stop musik.

**Keyboard**
* [ : Turunkan brightness (kecerahan) kamera.
* ] : Naikkan brightness kamera.
* q : Keluar dari program.

**Suara**
Jika sistem bertanya "Mau aku putarkan musik?", jawablah dengan jelas "Ya", "Mau", atau "Oke" di dekat mikrofon untuk memutar musik.
