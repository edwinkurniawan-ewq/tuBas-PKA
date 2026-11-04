# Tsaritsa: Searching for Gnosis 👑♟️

**Tsaritsa: Searching for Gnosis** adalah game pemecahan masalah *N-Queens Problem* yang dibungkus dengan tema cerita Genshin Impact (*Tsaritsa vs Phanes*) menggunakan kerangka kerja Pygame. Project ini dikembangkan untuk tugas besar mata kuliah Pengantar Kecerdasan Artifisial.

---

## 📌 Rules & Workflow Kelompok

Untuk menjaga kerapian repositori dan stabilitas kode di branch utama, seluruh anggota kelompok **WAJIB** mematuhi aturan berkontribusi berikut:

1. **Aturan Commit Message:** Setiap *commit* harus menyertakan pesan yang jelas dan spesifik mengenai perubahan atau fitur yang ditambahkan/diperbaiki.
   * *Contoh yang baik:* `git commit -m "feat: menambahkan fitur hint bantuan Tsaritsa"`
   * *Contoh yang dilarang:* `git commit -m "update"` atau `git commit -m "fix bug"`

2. **Larangan Push Langsung ke Branch `main`:**
   * Dilarang keras melakukan `git push` langsung ke branch `main` tanpa persetujuan / review.
   * Seluruh perubahan pada branch `main` harus melalui *Pull Request* (PR) / *Merge Request* (MR) yang di-approve oleh pengelola repositori.

3. **Workflow Alur Kerja (Branching & Testing):**
   * **Langkah 1:** Buat branch fitur/perbaikan baru tersendiri dari branch main.
     ```bash
     git checkout -b fitur-nama-anggota
     # Contoh: git checkout -b feature-tsaritsa-hint
     ```
   * **Langkah 2:** Kerjakan perubahan dan lakukan *testing* secara lokal sampai kode berjalan stabil tanpa error.
   * **Langkah 3:** Commit dan push branch Anda ke GitHub.
     ```bash
     git add .
     git commit -m "penjelasan fitur/perubahan yang dibuat"
     git push origin feature-tsaritsa-hint
     ```
   * **Langkah 4:** Buka repository di GitHub dan buat **Pull Request (PR)** ke branch `main`.
   * **Langkah 5:** Tunggu *code review* dan *approval* sebelum dilakukan merge ke `main`.

---

## 🚀 Progress & Status Proyek

### 📊 Progress Awal (Saat Ini)
- [x] **Inisialisasi Antarmuka (GUI):** Pengoperasian papan N-Queens interaktif menggunakan `Pygame`.
- [x] **Aset Visual Awal:** Penambahan aset gambar bidak Gnosis (Anemo, Cryo, Dendro, Electro, Geo, Hydro, Pyro).
- [x] **Visual Novel Prototype:** Mode prolog cerita singkat antara Phanes dan Tsaritsa.
- [x] **Logika AI Dasar:** Implementasi 3 algoritma pencarian:
  - Depth-First Search (DFS)
  - Hill Climbing (HC)
  - Min-Conflicts (MC)
- [x] **Fitur Mode Permainan:** Solo Player, Solo vs Phanes, dan Benchmark Agent vs Agent.

---

## 🎯 Roadmap & Rencana Update Mendatang

Berikut adalah daftar fitur dan perbaikan yang perlu dikerjakan untuk update selanjutnya:

* [ ] **Peningkatan GUI:** Mempercantik tata letak (layout), tombol, serta tampilan papan catur.
* [ ] **Optimasi & Perbaikan Algoritma:** Refactoring dan perbaikan efisiensi pada ketiga algoritma AI (DFS, Hill Climbing, Min-Conflicts).
* [ ] **Perbaikan Animasi Min-Conflicts:** Memperbaiki sistem visualisasi langkah demi langkah (*step-by-step*) khusus untuk algoritma Min-Conflicts agar berjalan lancar.
* [ ] **Peningkatan Aset Gambar & Ekspresi Karakter:**
  - Menambahkan sprite karakter Phanes & Tsaritsa dengan berbagai ekspresi raut muka (*expressions*).
  - Menambahkan dialog visual novel yang lebih kaya dan interaktif.
* [ ] **Fitur QoL (Quality of Life):**
  - Implementasi **"Bantuan Tsaritsa"** (Hint system) pada mode *Solo Player* dan *Solo vs Phanes* untuk mempermudah pemain dalam menyelesaikan papan N-Queens.

---

## 🛠️ Cara Menjalankan Program

1. **Prasyarat System:** Pastikan Python 3.x dan Pygame sudah terinstall.
   ```bash
   pip install pygame
   ```

2. **Jalankan Game:**
   ```bash
   python N-quenn.py
   ``` 
