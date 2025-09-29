# 📚 AI Question Generator dari Materi Ajar - Lengkap dengan Jawaban & Analytic

Sistem AI Question Generator yang dirancang untuk memudahkan membuat soal, dengan tidak keluar dengan materi yang di upload.

## 🌟 Fitur Utama

- AI Question Generator : Sistem Untuk membuat soal dengan cepat
- Dashboard Interaktif : Visualisasi data dari soal
- Upload file : Form upload materi ajar
- Generate soal : Generate soal dengan menggunakan kata kunci yang penting
- Analytics : Analisis tingkat kesulitan soal dan waktu pembuatan
- Download : Fitur download dengan berbagai extension

## 🛠️ Teknologi dan library yang digunakan

- Python : Python 3.8+
- Streamlit : versi 1.28.0
- PyPDF2 : Versi 3.0.1
- Python-docx : Version 0.8.11
- Openai : Version 0.28.0
- Standard Python Libraries : re, random, typing, dataclasses, io, stringIO

## Run Locally

Clone the project

```bash
  git clone [URL_REPOSITORY]
```

Go to the project directory

```bash
  cd final-_project_ai_generator
```

Install dependencies

```bash
  final-_project_ai_generator
```

Start the server

```bash
  streamlit run app.py
```

## 📊 Struktur Proyek

```bash
├── 📄 app.py                                # Main aplikasi Streamlit
├── 📄 requirements.txt                      # Dependencies
├── 📄 README.md                             # Dokumentasi
└── 📄 .gitignore                            # File ignore untuk Git
└── 📄 contoh_materi.txt                     # File ignore untuk Git
```

## 📱 Halaman Aplikasi

- <b>Halaman dasboard</b>: manampilkan halaman dasboard, fitur upload, jumlah soal yang diinginkan, dan generate soal

- <b>halaman generate soal</b> : menanmpilkan hasil soal yang digenerate

- <b>halaman analytics</b> : menanmpilkan hasil Analytics & Insights

- <b>halaman analytics</b> : menanmpilkan fitur download soal, json, csv, txt

## 💡 CARA KERJA APLIKASI SAAT INI

<b>Model yang berjalan:</b>

- Input: User upload materi PDF/DOCX/TXT
- Processing: Extract teks → pisah kalimat → cari kata kunci
- Generation: Buat soal fill-in-the-blank dari kalimat
- Output: Soal pilihan ganda

<b>Dataset yang Dipakai:</b>

- 100% dari materi user - tidak butuh dataset eksternal
- Real-time processing - tidak butuh training sebelumnya
- Context-aware - soal sesuai dengan materi yang diupload

## 🤝 Kontribusi

Kontribusi selalu diterima! Silakan buat pull request atau laporkan issues jika menemukan bug.

## Aplikasi

https://final-project-a-i-generator.streamlit.app/
