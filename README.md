VocaFlow
VocaFlow adalah aplikasi desktop berbasis Python dan PySide6 yang digunakan untuk mengelola kosakata multibahasa dan hafalan bebas secara terstruktur. 
Aplikasi ini dilengkapi dengan fitur kuis, reminder, dan statistik progres untuk mendukung proses belajar yang konsisten dan terukur.

Teknologi yang Digunakan
Python
PySide6 (GUI Desktop)
Supabase (Backend dan Database)
REST API (komunikasi data)

Struktur File Utama
- main.py
  Berfungsi sebagai entry point aplikasi. File ini menginisialisasi aplikasi, menampilkan WelcomeWindow, dan mengatur alur utama antar halaman.

- welcome_window.py
  Mengatur tampilan halaman awal aplikasi yang berisi tombol Login dan Registrasi serta navigasi awal pengguna.

- register_window.py
  Berisi logika dan antarmuka pembuatan akun baru, termasuk validasi input dan hashing password menggunakan PBKDF2.

- login_window.py
  Menangani proses login pengguna dengan verifikasi password dan pengambilan user_id sebelum masuk ke dashboard.

- dashboard_window.py
  Merupakan menu utama aplikasi yang menyediakan navigasi ke seluruh fitur dan menjalankan ReminderService.

- folder_page.py
  Mengelola fitur kategori atau folder, termasuk tambah, ubah, hapus folder, serta menampilkan isi folder berupa kosakata dan hafalan bebas.

- notes_page.py
  Mengelola hafalan bebas, mulai dari penambahan catatan, pengeditan, penghapusan, filter folder, filter status hafal, hingga update cepat status hafal melalui tabel.

- vocabulary_page.py
  Mengelola kosakata multibahasa berbasis konsep, termasuk penyimpanan detail per bahasa, penghapusan bahasa tertentu, penghapusan seluruh kosakata, dan penandaan status hafal.

- quiz_page.py
  Mengimplementasikan quiz kosakata multibahasa dengan pemilihan bahasa sumber dan tujuan, pemeriksaan jawaban, perhitungan skor, serta update otomatis status hafal.

- notes_quiz_page.py
  Mengelola quiz hafalan bebas berbasis catatan yang belum hafal dengan metode self-assessment (benar atau salah).

- reminder_page.py
  Mengelola fitur reminder, termasuk penambahan, pembaruan, penghapusan, dan penandaan selesai melalui checkbox.

- reminder_service.py
  Menjalankan layanan background berbasis timer untuk mengecek reminder jatuh tempo dan menampilkan popup notifikasi di dashboard.

- statistic_page.py
  Mengambil dan menampilkan ringkasan data progres pengguna, seperti jumlah kosakata, hafalan bebas, folder, translation per bahasa, dan reminder.

- supabase_client.py
  Berisi konfigurasi koneksi ke Supabase dan fungsi-fungsi helper untuk melakukan operasi CRUD ke database.

- config.py
  Menyimpan konfigurasi aplikasi seperti URL Supabase, API key, dan pengaturan global lainnya.
