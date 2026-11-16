import subprocess

# Rangkaian input otomatis komprehensif untuk menguji seluruh fitur di main.py:
# - Sesi 1: Login Admin -> Keluar
# - Sesi 2: Login Petugas Gudang -> Barang Masuk, Barang Keluar, Opname -> Keluar
# - Sesi 3: Login Kasir -> Transaksi, Validasi Kuota (Ditolak & Diterima), Pembayaran -> Keluar
# - Keluar dari aplikasi utama

comprehensive_inputs = "\n".join([
    # --- SESI 1: ADMIN ---
    "admin",             # Username Admin
    "admin123",          # Password Admin
    "2",                 # Menu Admin: Atur Harga & Ketentuan Komoditas
    "12000",             # Ubah HET baru
    "4",                 # Logout Admin

    # --- SESI 2: PETUGAS GUDANG ---
    "gudang",            # Username Petugas Gudang
    "gudang123",         # Password Petugas Gudang
    "1",                 # Menu Gudang: Barang Masuk / Keluar / Opname
    "1",                 # Sub-menu: Barang Masuk (Restock)
    "BRG-001",           # Kode Barang
    "SUP-01",            # Kode Supplier
    "20",                # Jumlah Barang Masuk
    "SJ-2026-001",       # Nomor Referensi Surat Jalan
    "11000",             # Harga Beli Satuan
    "Pasokan rutin bulanan", # Keterangan
    
    # Lanjut uji Barang Keluar di menu gudang
    "1",                 # Menu Gudang lagi
    "2",                 # Sub-menu: Barang Keluar (Rusak/Expired)
    "BRG-001",           # Kode Barang
    "2",                 # Jumlah Keluar
    "rusak",             # Tujuan / Alasan Keluar
    "Bagian Display",    # Penerima
    "Kemasan robek",     # Keterangan
    
    # Lanjut uji Stock Opname di menu gudang
    "1",                 # Menu Gudang lagi
    "3",                 # Sub-menu: Penyesuaian Stok (Stock Opname)
    "BRG-001",           # Kode Barang
    "40",                # Stok Fisik Hasil Opname
    "Koreksi Opname Bulanan", # Alasan Penyesuaian
    "Hasil opname bersama tim gudang", # Keterangan
    "4",                 # Logout Petugas Gudang

    # --- SESI 3: KASIR & TRANSAKSI ---
    "kasir",             # Username Kasir
    "kasir123",          # Password Kasir
    "1",                 # Menu Kasir: Buat Transaksi Baru
    "Siti Rahma",        # Nama Pembeli
    "3201123456780009",  # NIK Pembeli
    "Jl. Mawar No. 12",  # Alamat Pembeli
    # Uji Item 1: Sengaja beli 6 (Melebihi batas maksimal transaksi = 5) untuk menguji penolakan kuota
    "BRG-001",           # Kode Barang
    "6",                 # Jumlah Beli (Melebihi batas)
    # Uji Item 2: Beli 3 (Sah sesuai kuota)
    "BRG-001",           # Kode Barang
    "3",                 # Jumlah Beli (Valid)
    "selesai",           # Selesai memasukkan item ke keranjang
    "50000",             # Nominal Uang Pembayaran Tunai
    "2",                 # Logout Kasir

    # --- KELUAR APLIKASI ---
    "keluar"             # Keluar dari program utama
])

print("==========================================================")
print("   MENJALANKAN SIMULASI OTOMATIS KOMPREHENSIF (SIMIP)      ")
print("==========================================================")

try:
    process = subprocess.Popen(
        ["python", "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    stdout, stderr = process.communicate(input=comprehensive_inputs, timeout=15)

    print("\n[HASIL EKSEKUSI PROGRAM]:")
    print(stdout)

    if stderr:
        print("\n[CATATAN ERROR / STDERR]:")
        print(stderr)

except subprocess.TimeoutExpired:
    process.kill()
    print("\n[ERROR]: Simulasi terhenti karena melebihi batas waktu (Timeout). Periksa apakah ada input terminal yang macet.")
except Exception as e:
    print(f"\n[ERROR]: Terjadi kesalahan saat menjalankan proses: {e}")