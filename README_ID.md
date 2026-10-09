# WargaHub Web MVP

Aplikasi web responsif untuk direktori UMKM, barang hilang/temuan, dan laporan lingkungan.

## Isi
- `app.py`: aplikasi Flask
- `templates/`: halaman web
- `static/style.css`: tampilan responsif
- `supabase_setup.sql`: struktur tabel dan kebijakan akses demo
- `render.yaml`: konfigurasi deploy Render
- `requirements.txt`: dependensi

## Jalankan lokal
1. Install Python 3.11+.
2. Buka terminal di folder proyek.
3. Buat virtual environment (opsional):
   - Windows: `python -m venv .venv`
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
4. Install dependensi: `pip install -r requirements.txt`
5. Buat project di Supabase, buka SQL Editor, lalu jalankan seluruh isi `supabase_setup.sql`.
6. Atur environment variables di terminal PowerShell:
   - `$env:SUPABASE_URL="https://PROJECT-ID.supabase.co"`
   - `$env:SUPABASE_KEY="SUPABASE_ANON_KEY"`
   - `$env:FLASK_SECRET_KEY="ganti-dengan-string-acak"`
7. Jalankan: `python app.py`
8. Buka `http://127.0.0.1:5000`

## Hosting gratis dengan Render
1. Upload folder proyek ke repository GitHub baru.
2. Di Supabase, jalankan `supabase_setup.sql` dan salin Project URL serta anon/public key.
3. Di Render, pilih New > Web Service dan hubungkan repository GitHub.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`
6. Pilih Free plan.
7. Tambahkan Environment Variables:
   - `SUPABASE_URL` = Project URL Supabase
   - `SUPABASE_KEY` = anon/public key
   - `FLASK_SECRET_KEY` = string acak panjang
   - `PYTHON_VERSION` = `3.13.5`
8. Deploy. Setelah selesai, gunakan URL `https://nama-aplikasi.onrender.com`.

## Catatan penting keamanan
- SQL ini membuka akses baca dan tambah data kepada publik demi demo MVP. Jangan gunakan dengan data pribadi sensitif atau sebagai layanan produksi tanpa autentikasi, moderasi, validasi, rate limiting, dan kebijakan privasi.
- Jangan pernah menaruh `service_role` key Supabase di kode atau di browser. Gunakan hanya anon/public key sebagai environment variable server.
- Nomor kontak yang dimasukkan akan ditampilkan kepada pengunjung. Pastikan pemilik nomor memberikan izin.
- Free web services Render dapat tidur setelah tidak aktif dan membutuhkan waktu untuk bangun. Database Supabase Free memiliki kuota/batas penggunaan yang dapat berubah.
