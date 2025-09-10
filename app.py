from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- Helper database ---
def get_db():
    conn = sqlite3.connect("kasir.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Setup database (menu & transaksi) ---
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    harga INTEGER,
    kategori TEXT
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER,
    jumlah INTEGER,
    total INTEGER,
    tanggal TEXT
)
""")
conn.commit()
conn.close()

# --- Routes ---
@app.route("/")
def index():
    conn = get_db()
    menu = conn.execute("SELECT * FROM menu").fetchall()
    transaksi = conn.execute("""
        SELECT t.id, m.nama, m.kategori, t.jumlah, t.total, t.tanggal
        FROM transaksi t
        JOIN menu m ON t.menu_id = m.id
    """).fetchall()
    conn.close()
    return render_template("index.html", menu=menu, transaksi=transaksi)

@app.route("/tambah_menu", methods=["POST"])
def tambah_menu():
    nama = request.form["nama"]
    harga = request.form["harga"]
    kategori = request.form["kategori"]
    conn = get_db()
    conn.execute("INSERT INTO menu (nama, harga, kategori) VALUES (?, ?, ?)", 
                 (nama, harga, kategori))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/hapus_menu/<int:id>")
def hapus_menu(id):
    conn = get_db()
    conn.execute("DELETE FROM menu WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/tambah_transaksi", methods=["POST"])
def tambah_transaksi():
    menu_id = request.form["menu_id"]
    jumlah = int(request.form["jumlah"])
    conn = get_db()
    menu = conn.execute("SELECT * FROM menu WHERE id=?", (menu_id,)).fetchone()
    total = menu["harga"] * jumlah
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO transaksi (menu_id, jumlah, total, tanggal) VALUES (?, ?, ?, ?)", 
                 (menu_id, jumlah, total, tanggal))
    conn.commit()
    conn.close()
    return redirect("/")

import sqlite3

def cek_dan_update_database():
    conn = sqlite3.connect("kasir.db")
    cursor = conn.cursor()

    # cek apakah kolom kategori ada
    cursor.execute("PRAGMA table_info(menu)")
    kolom = [c[1] for c in cursor.fetchall()]

    if "kategori" not in kolom:
        print("Kolom 'kategori' belum ada, menambahkan...")
        cursor.execute("ALTER TABLE menu ADD COLUMN kategori TEXT")
        conn.commit()

    conn.close()

if __name__ == '__main__':
    cek_dan_update_database()
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
