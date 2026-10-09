import os
import re
from datetime import datetime
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, flash
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "ganti-secret-key-untuk-demo")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()
supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def today():
    return datetime.now().strftime("%d-%m-%Y")

def clean_phone(phone):
    return re.sub(r"\D", "", phone or "")

def wa_link(phone, message):
    digits = clean_phone(phone)
    if digits.startswith("0"):
        digits = "62" + digits[1:]
    elif digits.startswith("8"):
        digits = "62" + digits
    return f"https://wa.me/{digits}?text={quote(message)}"

def get_rows(table, search=""):
    if not supabase:
        return []
    query = supabase.table(table).select("*").order("created_at", desc=True)
    if search.strip():
        term = search.strip().replace(",", " ")
        # Basic cross-field search; filtering is performed locally for this small MVP.
    response = query.execute()
    rows = response.data or []
    if search.strip():
        key = search.lower().strip()
        rows = [r for r in rows if key in " ".join(str(v or "") for v in r.values()).lower()]
    return rows

def insert_row(table, payload):
    if not supabase:
        raise RuntimeError("Database belum dihubungkan. Isi SUPABASE_URL dan SUPABASE_KEY.")
    supabase.table(table).insert(payload).execute()

@app.context_processor
def inject_globals():
    return {"db_ready": supabase is not None}

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    try:
        reports = get_rows("reports", q)
        businesses = get_rows("umkm", q)
        lost_items = get_rows("lost_found", q)
        error = None
    except Exception as e:
        reports, businesses, lost_items = [], [], []
        error = "Data belum dapat dimuat. Periksa pengaturan database Supabase dan kebijakan tabel."
    return render_template("index.html", reports=reports, businesses=businesses,
                           lost_items=lost_items, q=q, error=error)

@app.route("/umkm/tambah", methods=["GET", "POST"])
def add_umkm():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()
        description = request.form.get("description", "").strip()
        if not all([name, category, address, phone]):
            flash("Nama usaha, kategori, alamat, dan nomor kontak wajib diisi.", "error")
            return render_template("form_umkm.html")
        if len(clean_phone(phone)) < 9:
            flash("Nomor kontak tampaknya tidak valid. Periksa kembali.", "error")
            return render_template("form_umkm.html")
        try:
            insert_row("umkm", {"name": name, "category": category, "address": address,
                                "phone": phone, "description": description, "created_at": datetime.utcnow().isoformat()})
            flash("UMKM berhasil ditambahkan.", "success")
            return redirect(url_for("index"))
        except Exception:
            flash("Gagal menyimpan UMKM. Pastikan database Supabase sudah disiapkan.", "error")
    return render_template("form_umkm.html")

@app.route("/barang/tambah", methods=["GET", "POST"])
def add_lost_found():
    if request.method == "POST":
        item = request.form.get("item", "").strip()
        kind = request.form.get("kind", "").strip()
        location = request.form.get("location", "").strip()
        phone = request.form.get("phone", "").strip()
        description = request.form.get("description", "").strip()
        if not all([item, kind, location, phone]):
            flash("Nama barang, jenis, lokasi, dan nomor kontak wajib diisi.", "error")
            return render_template("form_barang.html")
        if len(clean_phone(phone)) < 9:
            flash("Nomor kontak tampaknya tidak valid. Periksa kembali.", "error")
            return render_template("form_barang.html")
        try:
            insert_row("lost_found", {"item": item, "kind": kind, "location": location,
                                      "phone": phone, "description": description, "created_at": datetime.utcnow().isoformat()})
            flash("Informasi barang berhasil ditambahkan.", "success")
            return redirect(url_for("index"))
        except Exception:
            flash("Gagal menyimpan informasi. Pastikan database Supabase sudah disiapkan.", "error")
    return render_template("form_barang.html")

@app.route("/laporan/tambah", methods=["GET", "POST"])
def add_report():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        if not all([title, category, location]):
            flash("Judul, kategori, dan lokasi wajib diisi.", "error")
            return render_template("form_laporan.html")
        try:
            insert_row("reports", {"title": title, "category": category, "location": location,
                                   "description": description, "status": "Menunggu",
                                   "created_at": datetime.utcnow().isoformat()})
            flash("Laporan lingkungan berhasil ditambahkan.", "success")
            return redirect(url_for("index"))
        except Exception:
            flash("Gagal menyimpan laporan. Pastikan database Supabase sudah disiapkan.", "error")
    return render_template("form_laporan.html")

@app.route("/health")
def health():
    return {"status": "ok", "database_connected": supabase is not None}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
