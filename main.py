from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal
import sys
from unittest.mock import patch

from models.pengguna.user import User
from models.pengguna.admin import Admin
from models.pengguna.kasir import Kasir
from models.pengguna.petugas_gudang import PetugasGudang

from models.inventaris.kategori import Kategori
from models.inventaris.supplier import Supplier
from models.inventaris.barang import Barang

from models.pembeli.pembeli import Pembeli
from models.pembeli.kualifikasi_pembeli import KualifikasiPembeli
from models.pembeli.aturan_penjualan import AturanPenjualan

from menu import menu_admin, menu_kasir, menu_petugas_gudang

def setup_initial_data():

    kat_sembako = Kategori("KAT-01", "Sembako & Pangan Bersubsidi", "Komoditas pangan program pemerintah")
    kat_energi = Kategori("KAT-02", "Energi Bersubsidi", "Tabung gas LPG 3 kg bersubsidi")
    kat_umum = Kategori("KAT-03", "Kebutuhan Umum", "Barang dagangan umum non-subsidi")

    sup_bulog = Supplier("SUP-01", "Perum Bulog", "BUMN_BULOG", "021-5252209", "Jakarta")
    sup_pertamina = Supplier("SUP-02", "Agen Gas Sejahtera", "AGEN_PERTAMINA", "08129876543", "Semarang")
    sup_umum = Supplier("SUP-03", "CV Distributor Makmur", "DISTRIBUTOR_UMUM", "08123456789", "Surabaya")

    aturan_sphp = AturanPenjualan(
        id_aturan="ATR-SPHP-01",
        kode_program_komoditas="BERAS_SPHP",
        harga_eceran_tertinggi=Decimal("62500"),
        batas_maksimal_per_transaksi=5,
        batas_maksimal_per_periode=5,
        periode_kuota="HARIAN",
        wajib_identitas_nik=False,
        daftar_kategori_pembeli_diizinkan=[],
        status_aktif=True
    )

    aturan_minyakita = AturanPenjualan(
        id_aturan="ATR-MYK-01",
        kode_program_komoditas="MINYAKITA",
        harga_eceran_tertinggi=Decimal("15700"),
        batas_maksimal_per_transaksi=5,
        batas_maksimal_per_periode=None,
        periode_kuota="HARIAN",
        wajib_identitas_nik=False,
        daftar_kategori_pembeli_diizinkan=[],
        status_aktif=True
    )

    aturan_lpg = AturanPenjualan(
        id_aturan="ATR-LPG-01",
        kode_program_komoditas="LPG_3KG",
        harga_eceran_tertinggi=Decimal("18000"),
        batas_maksimal_per_transaksi=2,
        batas_maksimal_per_periode=4,
        periode_kuota="MINGGUAN",
        wajib_identitas_nik=True,
        daftar_kategori_pembeli_diizinkan=[
            "RUMAH_TANGGA",
            "USAHA_MIKRO",
            "NELAYAN_SASARAN",
            "PETANI_SASARAN"
        ],
        status_aktif=True
    )

    daftar_barang = [
        Barang("BRG-001", "Beras SPHP 5kg", "Pak", Decimal("60000"), 30, 5, True, kat_sembako, aturan_sphp),
        Barang("BRG-002", "Minyakita 1 Liter", "Pouch", Decimal("15500"), 40, 10, True, kat_sembako, aturan_minyakita),
        Barang("BRG-003", "LPG Tabung 3 Kg", "Tabung", Decimal("17500"), 15, 5, True, kat_energi, aturan_lpg),
        Barang("BRG-004", "Gula Pasir Kemasan 1kg", "Kg", Decimal("16500"), 20, 5, True, kat_umum, None),
    ]

    users = {
        "admin": Admin("U-01", "admin", User.hash_password("admin123"), "Administrator Koperasi"),
        "kasir1": Kasir("U-02", "kasir1", User.hash_password("kasir123"), "Budi Santoso", "Pagi"),
        "kasir2": Kasir("U-03", "kasir2", User.hash_password("kasir123"), "Ani Wijaya", "Siang"),
        "gudang": PetugasGudang("U-04", "gudang", User.hash_password("gudang123"), "Siti Aminah")
    }

    pembeli_contoh = Pembeli(
        id_pembeli="CUST-001",
        nama_pembeli="Ahmad Subarjo",
        alamat_domisili="Jl. Merdeka No. 10, Desa Merah Putih",
        nik_terenkripsi="3374123456780001",
        tipe_pembeli_umum=False
    )
    pembeli_contoh.tambah_kualifikasi_komoditas(
        KualifikasiPembeli(
            id_kualifikasi="KUAL-001",
            kode_program_komoditas="LPG_3KG",
            kategori_sasaran="RUMAH_TANGGA",
            nomor_dokumen_pendukung="KK-3374010101900001",
            status_verifikasi=True,
            tanggal_berlaku_sampai=date.today() + timedelta(days=365)
        )
    )

    return (
        users,
        daftar_barang,
        [sup_bulog, sup_pertamina, sup_umum],
        [kat_sembako, kat_energi, kat_umum],
        [],
        [],
        [pembeli_contoh],
    )


def main_loop_core():
    users, daftar_barang, daftar_supplier, daftar_kategori, daftar_transaksi, daftar_aktivitas, daftar_pembeli = setup_initial_data()

    while True:
        print("\n============================================================")
        print("   SIMIP - KOPERASI DESA MERAH PUTIH (PRD v0.2 - CLI PBO)   ")
        print("============================================================")
        print("Akun Bawaan Demo:")
        print(" - Admin          : admin  / admin123")
        print(" - Kasir 1        : kasir1 / kasir123")
        print(" - Kasir 2        : kasir2 / kasir123")
        print(" - Petugas Gudang : gudang / gudang123")
        print("Ketik 'keluar' pada Username untuk menghentikan program.")

        username = input("\nUsername : ").strip()
        if username.lower() == "keluar":
            print("Terima kasih telah menggunakan SIMIP Kopdes Merah Putih.")
            sys.exit(0)

        password = input("Password : ").strip()

        user_obj = users.get(username)
        if user_obj and user_obj.login(username, password):
            print(f"\n[Login Berhasil] Selamat datang, {user_obj.nama_lengkap} (Peran: {user_obj.peran})")
            if isinstance(user_obj, Admin):
                menu_admin(user_obj, users, daftar_barang, daftar_kategori, daftar_supplier, daftar_transaksi, daftar_aktivitas)
            elif isinstance(user_obj, Kasir):
                menu_kasir(user_obj, daftar_barang, daftar_pembeli, daftar_transaksi)
            elif isinstance(user_obj, PetugasGudang):
                menu_petugas_gudang(user_obj, daftar_barang, daftar_supplier, daftar_aktivitas)
        else:
            print("[Login Gagal] Username/password salah atau akun dalam status NONAKTIF (FR-01).")



def jalankan_simulasi_otomatis_interaktif():
    """
    Menjalankan seluruh alur aplikasi secara otomatis dengan mensimulasikan
    input keyboard pengguna (mock_input) di semua peran dan skenario negatif/positif.
    """
    print("==================================================================")
    print("  SIMULASI OTOMATIS KOMPREHENSIF SIMIP PRD v0.2 (SEMUA SKENARIO)  ")
    print("==================================================================")

    simulated_inputs = [
        # --- 0. UJI LOGIN GAGAL (FR-01 / BR-01) ---
        "admin", "password_salah",

        # --- 1. LOGIN ADMIN: KELOLA PENGGUNA, MASTER BARANG, KATEGORI, SUPPLIER & ATURAN ---
        "admin", "admin123",
        "1", "tambah", "kasir_uji", "rahasia123", "Kasir Uji", "KASIR", "Malam",
        "1", "nonaktifkan", "kasir_uji",
        "7",                                                  # Logout sementara uji akun nonaktif
        "kasir_uji", "rahasia123",                            # Harus gagal login (NONAKTIF)
        "admin", "admin123",
        "1", "aktifkan", "kasir_uji",

        # Master Barang: uji kode duplikat, tambah barang, soft-delete, & ubah harga > HET
        "2", "tambah", "BRG-001",                             # Ditolak (BR-02 kode duplikat)
        "2", "tambah", "BRG-005", "Tepung Terigu 1kg", "Kg", "12000", "5", "3",
        "2", "tambah", "BRG-006", "Barang Uji Nonaktif", "Pcs", "5000", "2", "3",
        "2", "nonaktifkan", "BRG-006",
        "2", "ubah", "BRG-001", "Beras SPHP 5kg", "65000",    # Warning p = min(h, H)
        "4", "1", "BERAS_SPHP", "62500", "5", "5", "HARIAN", "n", "",

        # Kategori & Supplier
        "3", "kategori", "Bumbu Dapur", "Aneka bumbu masak",
        "3", "supplier", "PT Pangan Nusantara", "DISTRIBUTOR_UMUM", "0811223344", "Semarang",
        "7",                                                  # Logout Admin

        # --- 2. LOGIN PETUGAS GUDANG: MUTASI STOK & VALIDASI NEGATIF (FR-14..17) ---
        "gudang", "gudang123",
        "1", "5", "3", "25", "SJ-2026-099", "10500", "Stok awal tepung",
        "2", "4", "999", "RUSAK", "Staff", "Uji lebih stok",              # Ditolak stok kurang
        "2", "4", "2", "RUSAK", "Staff Gudang", "Kemasan gula sobek",
        "3", "3", "6", "Opname tabung gas", "Selisih fisik LPG",
        "4",                                                               # Lihat riwayat persediaan
        "5",                                                               # Logout Gudang

        # --- 3. LOGIN KASIR 1: UJI SELURUH SKENARIO PENJUALAN & REGULASI (FR-07..13) ---
        "kasir1", "kasir123",
        # 3A. Pembeli Umum: tolak stok kurang, tolak SPHP anonim, tolak LPG tanpa NIK, tolak kuota Minyakita
        "1", "1",
        "4", "999",                                           # Ditolak stok kurang
        "1", "2",                                             # Ditolak SPHP anonim
        "3", "1",                                             # Ditolak LPG tanpa NIK
        "2", "6",                                             # Ditolak Minyakita > batas 5
        "2", "3",                                             # Lolos Minyakita 3 pouch
        "4", "2",                                             # Lolos Gula 2 kg
        "bayar",
        "50000",                                              # Ditolak pembayaran kurang (tetap DRAFT)
        "100000",                                             # Lunas & cetak struk (SELESAI)

        # 3B. Pembeli Baru ber-NIK valid: beli SPHP 5 pak, tolak LPG tanpa kualifikasi
        "1", "3", "Siti Rahma", "3374123456780009", "Jl. Mawar No. 12",
        "1", "5",                                             # Lolos SPHP 5 pak
        "3", "1",                                             # Ditolak LPG tanpa kualifikasi
        "bayar",
        "350000",

        # 3C. Kualifikasi Kedaluwarsa & Kuota Harian SPHP Habis -> Batalkan Transaksi
        "2", "2", "LPG_3KG", "USAHA_MIKRO", "NIB-EXP", "-1",
        "1", "2", "2",
        "3", "1",                                             # Ditolak kualifikasi kedaluwarsa
        "1", "1",                                             # Ditolak kuota harian SPHP 5/5 habis
        "batal",                                              # Status DIBATALKAN

        # 3D. Kualifikasi LPG Aktif & Picu Peringatan Stok Minimum
        "2", "2", "LPG_3KG", "USAHA_MIKRO", "NIB-2026-88", "365",
        "1", "2", "2",
        "3", "2",                                             # Stok LPG 6 -> 4 (<= min 5, muncul BANNER!)
        "bayar",
        "50000",

        "3",                                                  # Riwayat penjualan Kasir 1
        "4",                                                  # Logout Kasir 1

        # --- 4. LOGIN KASIR 2: UJI ISOLASI RIWAYAT KASIR (RBAC O-18) ---
        "kasir2", "kasir123",
        "3",                                                  # Harus kosong (terisolasi)
        "4",                                                  # Logout Kasir 2

        # --- 5. LOGIN ADMIN: UJI HISTORICAL IMMUTABILITY, LAPORAN & AUDIT ---
        "admin", "admin123",
        "4", "1", "BERAS_SPHP", "55000", "5", "5", "HARIAN", "n", "",
        "5", "y",                                             # Laporan Penjualan & Persediaan kritis
        "6", "Siti", "SELESAI", "BRG-003",                    # Audit & filter pencarian
        "7",                                                  # Logout Admin

        # --- 6. KELUAR ---
        "keluar"
    ]

    def mock_input(prompt=''):
        print(prompt, end='')
        if simulated_inputs:
            val = simulated_inputs.pop(0)
            print(val)
            return val
        return "keluar"

    with patch('builtins.input', side_effect=mock_input):
        try:
            main_loop_core()
        except SystemExit:
            print("\n==================================================================")
            print("  SIMULASI OTOMATIS SELESAI MENJALANKAN SELURUH SKENARIO")
            print("==================================================================")


def main():
    jalankan_simulasi_otomatis_interaktif()


if __name__ == "__main__":
    main()