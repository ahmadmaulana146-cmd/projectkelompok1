"""
Sistem Manajemen Inventaris dan Penjualan (SIMIP)
Koperasi Desa Merah Putih (PRD v0.2 - Aplikasi CLI PBO)
Lokasi File: main.py
"""

from __future__ import annotations
from datetime import date, datetime, timedelta
from decimal import Decimal
import sys

# --- IMPOR 19 KELAS DOMAIN MURNI SESUAI ARSITEKTUR PROYEK ---
from models.pengguna.user import User
from models.pengguna.admin import Admin
from models.pengguna.kasir import Kasir
from models.pengguna.petugas_gudang import PetugasGudang

from models.inventaris.kategori import Kategori
from models.inventaris.supplier import Supplier
from models.inventaris.barang import Barang

from models.persediaan.aktivitas_persediaan import AktivitasPersediaan
from models.persediaan.barang_masuk import BarangMasuk
from models.persediaan.barang_keluar import BarangKeluar
from models.persediaan.penyesuaian_stok import PenyesuaianStok

from models.pembeli.pembeli import Pembeli
from models.pembeli.kualifikasi_pembeli import KualifikasiPembeli
from models.pembeli.aturan_penjualan import AturanPenjualan
from models.pembeli.hasil_validasi import HasilValidasi

from models.transaksi.transaksi_penjualan import TransaksiPenjualan
from models.transaksi.detail_transaksi import DetailTransaksi
from models.transaksi.pembayaran import Pembayaran
from models.transaksi.layanan_laporan import LayananLaporan


# =====================================================================
# 1. INISIALISASI DATA AWAL (IN-MEMORY COLLECTIONS & PARAMETER PRD §7)
# =====================================================================

def setup_initial_data():
    """Menginisialisasi data master awal dalam memori aktif sesuai regulasi PRD §7."""
    kat_sembako = Kategori("KAT-01", "Sembako & Pangan Bersubsidi", "Komoditas pangan program pemerintah")
    kat_energi = Kategori("KAT-02", "Energi Bersubsidi", "Tabung gas LPG 3 kg bersubsidi")
    kat_umum = Kategori("KAT-03", "Kebutuhan Umum", "Barang dagangan umum non-subsidi")

    sup_bulog = Supplier("SUP-01", "Perum Bulog", "BUMN_BULOG", "021-5252209", "Jakarta")
    sup_pertamina = Supplier("SUP-02", "Agen Gas Sejahtera", "AGEN_PERTAMINA", "08129876543", "Semarang")
    sup_umum = Supplier("SUP-03", "CV Distributor Makmur", "DISTRIBUTOR_UMUM", "08123456789", "Surabaya")

    # 1. Beras SPHP: HET Rp 62.500/pak (5kg), maks 5 pak/transaksi & 5 pak/hari, wajib terdaftar
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

    # 2. Minyakita: HET Rp 15.700/liter, batas transaksi 5 liter
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

    # 3. LPG 3 Kg: Wajib NIK & Kategori Sasaran
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


# =====================================================================
# 2. FUNGSI PEMBANTU LOGIKA BISNIS UMUM (KUOTA, VALIDASI & STOK)
# =====================================================================

def apakah_wajib_pembeli_terdaftar(aturan: AturanPenjualan | None) -> bool:
    """
    Mengecek secara umum apakah aturan penjualan mewajibkan pembeli terdaftar
    (tidak boleh Pembeli Umum/anonim), berlaku untuk program lama maupun produk baru.
    """
    if not aturan or not aturan.status_aktif:
        return False
    return bool(
        aturan.wajib_identitas_nik
        or aturan.batas_maksimal_per_periode is not None
        or len(aturan.daftar_kategori_pembeli_diizinkan) > 0
    )


def hitung_akumulasi_kuota_pembeli(pembeli: Pembeli, kode_program: str, periode_kuota: str, daftar_transaksi: list) -> int:
    """Menghitung total kuantitas pembelian berstatus SELESAI dalam jendela periode kuota."""
    if pembeli.tipe_pembeli_umum or not kode_program:
        return 0

    hari_ini = date.today()
    total_akumulasi = 0

    for tx in daftar_transaksi:
        if tx.status_transaksi != "SELESAI":
            continue
        if tx.pembeli.id_pembeli != pembeli.id_pembeli:
            continue

        tgl_tx = tx.waktu_transaksi.date()
        dalam_periode = False
        if periode_kuota == "HARIAN" and tgl_tx == hari_ini:
            dalam_periode = True
        elif periode_kuota == "MINGGUAN" and (hari_ini - tgl_tx).days < 7:
            dalam_periode = True
        elif periode_kuota == "BULANAN" and (tgl_tx.year == hari_ini.year and tgl_tx.month == hari_ini.month):
            dalam_periode = True

        if dalam_periode:
            for det in tx.daftar_detail:
                if det.kode_aturan_diterapkan == kode_program:
                    total_akumulasi += det.jumlah_beli

    return total_akumulasi


def cek_peringatan_stok_minimum(daftar_barang: list) -> list:
    """Menampilkan banner peringatan teks jika ada barang mencapai stok minimum (FR-17)."""
    barang_kritis = [b for b in daftar_barang if b.status_aktif and b.apakah_mencapai_batas_minimum()]
    if barang_kritis:
        print("\n" + "!" * 60)
        print("  [PERINGATAN STOK MINIMUM] Segera lakukan pengadaan ulang:")
        for b in barang_kritis:
            print(f"   * [{b.kode_barang}] {b.nama_barang} -> Sisa: {b.stok_tersedia} {b.satuan} (Min: {b.stok_minimum})")
        print("!" * 60)
    return barang_kritis


# =====================================================================
# 3. MODUL ANTARMUKA MENU ADMIN (FR-02 s.d. FR-06, FR-18 s.d. FR-20)
# =====================================================================

def menu_admin(admin: Admin, users: dict, daftar_barang: list, daftar_kategori: list, daftar_supplier: list, daftar_transaksi: list, daftar_aktivitas: list):
    while True:
        print("\n========================================================")
        print(f"  MENU ADMIN ({admin.nama_lengkap})")
        print("========================================================")
        print("1. Kelola Pengguna Sistem (FR-02)")
        print("2. Kelola Master Barang / Tambah Produk (FR-03)")
        print("3. Kelola Kategori & Supplier (FR-04, FR-05)")
        print("4. Tetapkan / Cabut Aturan Penjualan & HET Komoditas (FR-06)")
        print("5. Laporan Penjualan & Persediaan (FR-18)")
        print("6. Audit Riwayat Transaksi & Mutasi Stok (FR-19, FR-20)")
        print("7. Logout")
        pilih = input("Pilih menu (1-7): ").strip()

        if pilih == "1":
            print("\n--- DAFTAR PENGGUNA ---")
            for u in users.values():
                st = "AKTIF" if u.status_aktif else "NONAKTIF"
                print(f" - [{u.id_user}] {u.username} | {u.nama_lengkap} | Peran: {u.peran} | Status: {st}")

            aksi = input("\nAksi (tambah / aktifkan / nonaktifkan / kembali): ").strip().lower()
            try:
                if aksi == "tambah":
                    uname = input("Username baru: ").strip()
                    if uname in users:
                        print("[Error] Username sudah digunakan.")
                        continue
                    pwd = input("Password (min 6 karakter): ").strip()
                    if len(pwd) < 6:
                        print("[Error] Password minimal 6 karakter.")
                        continue
                    nama = input("Nama lengkap: ").strip()
                    peran = input("Peran (ADMIN / KASIR / PETUGAS_GUDANG): ").strip().upper()
                    uid = f"U-{len(users)+1:02d}"

                    if peran == "ADMIN":
                        u_baru = Admin(uid, uname, User.hash_password(pwd), nama)
                    elif peran == "KASIR":
                        shift = input("Shift kerja (Pagi/Siang/Malam): ").strip()
                        u_baru = Kasir(uid, uname, User.hash_password(pwd), nama, shift)
                    elif peran == "PETUGAS_GUDANG":
                        u_baru = PetugasGudang(uid, uname, User.hash_password(pwd), nama)
                    else:
                        print("[Error] Peran tidak valid.")
                        continue

                    admin.kelola_pengguna(u_baru, "tambah")
                    users[uname] = u_baru
                    print(f"[Sukses] Pengguna '{uname}' berhasil ditambahkan.")
                elif aksi in ("aktifkan", "nonaktifkan"):
                    uname = input("Masukkan username target: ").strip()
                    if uname not in users:
                        print("[Error] Username tidak ditemukan.")
                    elif uname == admin.username:
                        print("[Error] Tidak dapat menonaktifkan akun sendiri yang sedang login.")
                    else:
                        admin.kelola_pengguna(users[uname], aksi)
                        print(f"[Sukses] Status akun '{uname}' berhasil di-{aksi}.")
            except Exception as e:
                print(f"[Error] {e}")

        elif pilih == "2":
            print("\n--- DAFTAR MASTER BARANG ---")
            for b in daftar_barang:
                st = "AKTIF" if b.status_aktif else "NONAKTIF"
                prog = b.aturan_penjualan.kode_program_komoditas if b.aturan_penjualan else "UMUM"
                print(f" - [{b.kode_barang}] {b.nama_barang} | Kat: {b.kategori.nama_kategori if b.kategori else '-'} | "
                      f"Dasar: Rp {b.harga_dasar} | Jual: Rp {b.dapatkan_harga_berlaku()} | Stok: {b.stok_tersedia} {b.satuan} | Program: {prog} | [{st}]")

            aksi = input("\nAksi (tambah / ubah / aktifkan / nonaktifkan / kembali): ").strip().lower()
            try:
                if aksi == "tambah":
                    saran_kode = f"BRG-{len(daftar_barang)+1:03d}"
                    kode = input(f"Kode Barang unik (contoh {saran_kode}): ").strip().upper() or saran_kode
                    if any(b.kode_barang == kode for b in daftar_barang):
                        print("[Error] Kode barang sudah terdaftar (BR-02).")
                        continue
                    nama = input("Nama Produk: ").strip()
                    satuan = input("Satuan (Pak/Pouch/Tabung/Kg/Sak/Pcs/dll): ").strip()
                    harga = Decimal(input("Harga Dasar (Rp): ").strip())
                    stok_min = int(input("Batas Stok Minimum: ").strip())

                    print("Pilih Kategori:")
                    for i, k in enumerate(daftar_kategori):
                        print(f" [{i+1}] {k.nama_kategori}")
                    idx_k = int(input("Nomor kategori: ").strip()) - 1
                    kat_pilih = daftar_kategori[idx_k] if 0 <= idx_k < len(daftar_kategori) else None

                    brg_baru = Barang(kode, nama, satuan, harga, 0, stok_min, True, kat_pilih, None)
                    admin.kelola_barang(brg_baru, "tambah")
                    daftar_barang.append(brg_baru)
                    print(f"[Sukses] Produk '{nama}' ({kode}) ditambahkan dengan stok awal 0.")
                    print("[Info] Jika produk memiliki HET/kuota khusus, atur melalui Menu 4.")
                elif aksi == "ubah":
                    kode = input("Masukkan Kode Barang yang akan diubah: ").strip().upper()
                    brg = next((b for b in daftar_barang if b.kode_barang == kode), None)
                    if not brg:
                        print("[Error] Barang tidak ditemukan.")
                        continue
                    brg.nama_barang = input(f"Nama baru ({brg.nama_barang}): ").strip() or brg.nama_barang
                    h_str = input(f"Harga dasar baru (Rp {brg.harga_dasar}, Enter jika tetap): ").strip()
                    if h_str:
                        h_baru = Decimal(h_str)
                        brg.harga_dasar = h_baru
                        if brg.aturan_penjualan and brg.aturan_penjualan.harga_eceran_tertinggi:
                            if h_baru > brg.aturan_penjualan.harga_eceran_tertinggi:
                                print(f"[WARNING] Harga dasar (Rp {h_baru}) melebihi HET (Rp {brg.aturan_penjualan.harga_eceran_tertinggi}). "
                                      f"Harga jual otomatis dibatasi ke HET (p = min(h, H)).")
                    admin.kelola_barang(brg, "ubah")
                    print("[Sukses] Data barang diperbarui.")
                elif aksi in ("aktifkan", "nonaktifkan"):
                    kode = input(f"Masukkan Kode Barang yang akan di-{aksi}: ").strip().upper()
                    brg = next((b for b in daftar_barang if b.kode_barang == kode), None)
                    if brg:
                        admin.kelola_barang(brg, aksi)
                        print(f"[Sukses] Barang {brg.nama_barang} berhasil di-{aksi}.")
                    else:
                        print("[Error] Barang tidak ditemukan.")
            except Exception as e:
                print(f"[Error] {e}")

        elif pilih == "3":
            print("\n--- KATEGORI ---")
            for k in daftar_kategori:
                print(f" - [{k.id_kategori}] {k.nama_kategori}: {k.deskripsi}")
            print("\n--- SUPPLIER ---")
            for s in daftar_supplier:
                print(f" - [{s.id_supplier}] {s.nama_supplier} ({s.jenis_instansi}) | Telp: {s.kontak_telepon}")

            sub = input("\nTambah (kategori / supplier / kembali): ").strip().lower()
            try:
                if sub == "kategori":
                    kid = f"KAT-{len(daftar_kategori)+1:02d}"
                    knama = input("Nama Kategori: ").strip()
                    kdesk = input("Deskripsi: ").strip()
                    kat_baru = Kategori(kid, knama, kdesk)
                    admin.kelola_kategori(kat_baru, "tambah")
                    daftar_kategori.append(kat_baru)
                    print("[Sukses] Kategori ditambahkan.")
                elif sub == "supplier":
                    sid = f"SUP-{len(daftar_supplier)+1:02d}"
                    snama = input("Nama Supplier: ").strip()
                    sjenis = input("Jenis Instansi (BUMN_BULOG / AGEN_PERTAMINA / DISTRIBUTOR_UMUM / dll): ").strip().upper()
                    stelp = input("Telepon: ").strip()
                    salamat = input("Alamat: ").strip()
                    sup_baru = Supplier(sid, snama, sjenis, stelp, salamat)
                    admin.kelola_supplier(sup_baru, "tambah")
                    daftar_supplier.append(sup_baru)
                    print("[Sukses] Supplier ditambahkan.")
            except Exception as e:
                print(f"[Error] {e}")

        elif pilih == "4":
            print("\n--- PENGATURAN ATURAN PENJUALAN & HET ---")
            for i, b in enumerate(daftar_barang):
                het_info = f"[{b.aturan_penjualan.kode_program_komoditas}] HET Rp {b.aturan_penjualan.harga_eceran_tertinggi}" if b.aturan_penjualan else "Tidak Ada (Produk Umum)"
                print(f" [{i+1}] {b.nama_barang} | Harga Dasar: Rp {b.harga_dasar} | Aturan: {het_info}")
            try:
                idx = int(input("Pilih nomor barang: ").strip()) - 1
                if 0 <= idx < len(daftar_barang):
                    b = daftar_barang[idx]
                    mode_aturan = input("Aksi (atur / hapus_aturan): ").strip().lower() or "atur"
                    if mode_aturan == "hapus_aturan":
                        b.aturan_penjualan = None
                        print(f"[Sukses] Aturan khusus dicabut. {b.nama_barang} sekarang dijual sebagai produk umum.")
                        continue

                    prog = input("Kode Program Komoditas (mis. BERAS_SPHP / MINYAKITA / LPG_3KG / PUPUK_SUBSIDI): ").strip().upper()
                    het_baru = Decimal(input("Harga Eceran Tertinggi / HET baru (Rp): ").strip())
                    max_tx = int(input("Batas maksimal per transaksi (angka): ").strip())
                    max_per_str = input("Batas maksimal per periode (kosongkan jika tanpa batas): ").strip()
                    max_per = int(max_per_str) if max_per_str else None
                    periode = input("Periode kuota (HARIAN / MINGGUAN / BULANAN): ").strip().upper() or "HARIAN"
                    wajib_nik = input("Wajib verifikasi NIK 16 digit? (y/n): ").strip().lower() == "y"
                    kat_izin_str = input("Kategori sasaran diizinkan (pisahkan koma, mis. RUMAH_TANGGA,PETANI_SASARAN atau kosong): ").strip()
                    kat_izin = [x.strip().upper() for x in kat_izin_str.split(",") if x.strip()]

                    aturan_baru = AturanPenjualan(
                        id_aturan=f"ATR-{datetime.now().strftime('%H%M%S')}",
                        kode_program_komoditas=prog,
                        harga_eceran_tertinggi=het_baru,
                        batas_maksimal_per_transaksi=max_tx,
                        batas_maksimal_per_periode=max_per,
                        periode_kuota=periode,
                        wajib_identitas_nik=wajib_nik,
                        daftar_kategori_pembeli_diizinkan=kat_izin,
                        status_aktif=True
                    )
                    admin.tetapkan_aturan_penjualan(b, aturan_baru)
                    if b.harga_dasar > het_baru:
                        print(f"[WARNING] Harga dasar (Rp {b.harga_dasar}) > HET baru (Rp {het_baru}). Harga jual dibatasi ke Rp {het_baru}.")
                    print("[Sukses] Aturan penjualan baru berhasil diterapkan!")
            except Exception as e:
                print(f"[Error] {e}")

        elif pilih == "5":
            svc = LayananLaporan(daftar_transaksi, daftar_barang, daftar_aktivitas)
            hari_ini = date.today()
            awal_tahun = date(hari_ini.year, 1, 1)
            lap_jual = svc.hasilkan_laporan_penjualan(awal_tahun, hari_ini)
            print("\n================ LAPORAN PENJUALAN ================")
            print(f"Periode          : {lap_jual['periode_awal']} s.d. {lap_jual['periode_akhir']}")
            print(f"Transaksi Selesai: {lap_jual['jumlah_transaksi']}")
            print(f"Total Item Terjual: {lap_jual['total_item_terjual']}")
            print(f"Total Omset      : Rp {lap_jual['total_omset']}")

            print("\n================ LAPORAN PERSEDIAAN ===============")
            hanya_kritis = input("Tampilkan hanya barang stok kritis? (y/n): ").strip().lower() == "y"
            for st in svc.hasilkan_laporan_persediaan(hanya_kritis):
                flag = " [STOK KRITIS <= MIN]" if st["status_kritis"] else ""
                print(f" - [{st['kode_barang']}] {st['nama_barang']}: Stok={st['stok_tersedia']} {st['satuan']} (Min={st['stok_minimum']}){flag}")

        elif pilih == "6":
            svc = LayananLaporan(daftar_transaksi, daftar_barang, daftar_aktivitas)
            print("\n--- AUDIT RIWAYAT TRANSAKSI (SEMUA) ---")
            kunci = input("Cari kata kunci (nomor tx / pembeli / kasir, kosong=semua): ").strip()
            st_filter = input("Filter status (SELESAI / DIBATALKAN / DITOLAK, kosong=semua): ").strip()
            for tx in svc.cari_riwayat_transaksi(kunci, st_filter or None):
                print(f" - [{tx.nomor_transaksi}] {tx.waktu_transaksi.strftime('%Y-%m-%d %H:%M')} | Kasir: {tx.kasir.nama_lengkap} | "
                      f"Pembeli: {tx.pembeli.nama_pembeli} (NIK: {tx.pembeli.nik_tampil_masked or '-'}) | Status: {tx.status_transaksi} | Total: Rp {tx.total_tagihan}")

            print("\n--- AUDIT RIWAYAT PERSEDIAAN (SEMUA) ---")
            kd_filter = input("Filter kode barang (kosong=semua): ").strip()
            for akt in svc.cari_riwayat_persediaan(kd_filter or None, None):
                r = akt.dapatkan_ringkasan_audit()
                print(f" - [{r['id_aktivitas']}] {akt.__class__.__name__} | {r['nama_barang']} | "
                      f"Stok: {r['stok_sebelum']} -> {r['stok_sesudah']} ({r['jumlah_perubahan']:+d}) | Petugas: {r['nama_petugas']}")

        elif pilih == "7":
            admin.logout()
            print("[Info] Logout dari akun Admin.")
            break
        else:
            print("[Error] Pilihan tidak valid.")


# =====================================================================
# 4. MODUL ANTARMUKA MENU KASIR (FR-07 s.d. FR-13, MATRIKS O-18)
# =====================================================================

def menu_kasir(kasir: Kasir, daftar_barang: list, daftar_pembeli: list, daftar_transaksi: list):
    while True:
        print("\n========================================================")
        print(f"  MENU KASIR ({kasir.nama_lengkap} - Shift {kasir.shift_kerja})")
        print("========================================================")
        print("1. Transaksi Penjualan Baru (FR-07 s.d. FR-13)")
        print("2. Daftarkan Kualifikasi Komoditas Pembeli (FR-08)")
        print("3. Riwayat Penjualan Saya (FR-19, FR-20)")
        print("4. Logout")
        pilih = input("Pilih menu (1-4): ").strip()

        if pilih == "1":
            print("\n--- LANGKAH 1: PILIH ATAU CATAT PEMBELI ---")
            print(" [1] Pembeli Umum (Anonim tanpa NIK)")
            print(" [2] Pilih Pembeli Terdaftar")
            print(" [3] Catat Pembeli Baru")
            opsi_p = input("Pilih jenis pembeli (1-3): ").strip()

            pembeli_aktif = None
            try:
                if opsi_p == "1":
                    pembeli_aktif = kasir.catat_data_pembeli(nama="Pembeli Umum", nik=None, alamat="-")
                elif opsi_p == "2":
                    if not daftar_pembeli:
                        print("[Info] Belum ada pembeli terdaftar.")
                        continue
                    for idx, p in enumerate(daftar_pembeli):
                        print(f" [{idx+1}] {p.nama_pembeli} | NIK: {p.nik_tampil_masked or 'Tidak Ada'} | Alamat: {p.alamat_domisili}")
                    idx_p = int(input("Pilih nomor pembeli: ").strip()) - 1
                    if 0 <= idx_p < len(daftar_pembeli):
                        pembeli_aktif = daftar_pembeli[idx_p]
                    else:
                        print("[Error] Nomor pembeli tidak valid.")
                        continue
                elif opsi_p == "3":
                    nama_p = input("Nama Lengkap Pembeli: ").strip()
                    nik_p = input("NIK (16 digit numerik, kosongkan jika tidak ada): ").strip()
                    if nik_p and (not nik_p.isdigit() or len(nik_p) != 16):
                        print("[Error] NFR-03: NIK harus berupa 16 digit numerik.")
                        continue
                    alamat_p = input("Alamat Domisili: ").strip()
                    pembeli_aktif = kasir.catat_data_pembeli(nama=nama_p, nik=nik_p or None, alamat=alamat_p)
                    daftar_pembeli.append(pembeli_aktif)
                    print(f"[Sukses] Pembeli terdaftar (NIK tersamar: {pembeli_aktif.nik_tampil_masked or '-'}).")
                else:
                    print("[Error] Pilihan tidak valid.")
                    continue
            except Exception as e:
                print(f"[Error] {e}")
                continue

            transaksi = kasir.buat_transaksi_baru(pembeli=pembeli_aktif)
            print(f"\n[Sukses] Draft Transaksi dibuat: {transaksi.nomor_transaksi}")

            while True:
                print("\n--- DAFTAR BARANG AKTIF ---")
                barang_aktif = [b for b in daftar_barang if b.status_aktif]
                for idx, b in enumerate(barang_aktif):
                    prog = f" [{b.aturan_penjualan.kode_program_komoditas}]" if b.aturan_penjualan else ""
                    print(f" [{idx+1}] {b.nama_barang}{prog} | Stok: {b.stok_tersedia} {b.satuan} | Harga: Rp {b.dapatkan_harga_berlaku()}")

                pilih_b = input("\nPilih nomor barang (atau ketik 'bayar' / 'batal'): ").strip().lower()
                if pilih_b == "bayar":
                    break
                if pilih_b == "batal":
                    transaksi.batalkan_transaksi("Dibatalkan oleh kasir sebelum pembayaran.")
                    daftar_transaksi.append(transaksi)
                    print("[Info] Transaksi dibatalkan.")
                    break

                try:
                    idx_b = int(pilih_b) - 1
                    if not (0 <= idx_b < len(barang_aktif)):
                        print("[Error] Nomor barang tidak valid.")
                        continue

                    brg = barang_aktif[idx_b]
                    jml = int(input(f"Masukkan jumlah beli ({brg.satuan}): ").strip())

                    # Validasi umum berdasarkan sifat aturan penjualan (tanpa hardcode nama program)
                    if apakah_wajib_pembeli_terdaftar(brg.aturan_penjualan) and pembeli_aktif.tipe_pembeli_umum:
                        print(f"[DITOLAK] Komoditas {brg.aturan_penjualan.kode_program_komoditas} mewajibkan pembeli terdaftar (bukan Pembeli Umum).")
                        continue

                    akumulasi = 0
                    if brg.aturan_penjualan:
                        akumulasi = hitung_akumulasi_kuota_pembeli(
                            pembeli=pembeli_aktif,
                            kode_program=brg.aturan_penjualan.kode_program_komoditas,
                            periode_kuota=brg.aturan_penjualan.periode_kuota,
                            daftar_transaksi=daftar_transaksi
                        )

                    item_existing = next((d for d in transaksi.daftar_detail if d.barang.kode_barang == brg.kode_barang), None)
                    if item_existing:
                        total_jml_baru = item_existing.jumlah_beli + jml
                        transaksi.hapus_item_barang(brg.kode_barang)
                        hasil = transaksi.tambah_item_barang(barang=brg, jumlah=total_jml_baru, akumulasi_periode=akumulasi)
                        if not hasil.apakah_lolos():
                            transaksi.tambah_item_barang(barang=brg, jumlah=item_existing.jumlah_beli, akumulasi_periode=akumulasi)
                            print(f"[DITOLAK] {hasil.pesan_validasi}")
                        else:
                            print(f"[Berhasil] Kuantitas {brg.nama_barang} diperbarui menjadi {total_jml_baru} {brg.satuan}.")
                            print(f"Subtotal Tagihan Sementara: Rp {transaksi.total_tagihan}")
                    else:
                        hasil = transaksi.tambah_item_barang(barang=brg, jumlah=jml, akumulasi_periode=akumulasi)
                        if hasil.apakah_lolos():
                            print(f"[Berhasil] {hasil.pesan_validasi}")
                            print(f"Subtotal Tagihan Sementara: Rp {transaksi.total_tagihan}")
                        else:
                            print(f"[DITOLAK] {hasil.pesan_validasi}")

                except ValueError as e:
                    print(f"[Error] Input tidak valid: {e}")

            if transaksi.status_transaksi == "DRAFT":
                if len(transaksi.daftar_detail) == 0:
                    transaksi.batalkan_transaksi("Keranjang belanja kosong.")
                    daftar_transaksi.append(transaksi)
                    print("[Info] Keranjang kosong, transaksi dibatalkan otomatis.")
                else:
                    print("\n================ RINGKASAN TAGIHAN ================")
                    for d in transaksi.daftar_detail:
                        print(f" - {d.barang.nama_barang} ({d.jumlah_beli} x Rp {d.harga_satuan_saat_transaksi}) = Rp {d.subtotal}")
                    print(f"TOTAL TAGIHAN: Rp {transaksi.total_tagihan}")

                    while True:
                        try:
                            bayar_str = input("Masukkan nominal tunai diterima (Rp) atau 'batal': ").strip()
                            if bayar_str.lower() == "batal":
                                transaksi.batalkan_transaksi("Pembayaran dibatalkan kasir.")
                                daftar_transaksi.append(transaksi)
                                print("[Info] Transaksi dibatalkan.")
                                break

                            nominal_bayar = Decimal(bayar_str)
                            pembayaran = transaksi.proses_pembayaran(nominal_bayar=nominal_bayar, metode="TUNAI")
                            transaksi.selesaikan_transaksi()
                            daftar_transaksi.append(transaksi)

                            print("\n" + "=" * 50)
                            print("       STRUK PEMBAYARAN - KOPDES MERAH PUTIH      ")
                            print("=" * 50)
                            print(f"No. Transaksi : {transaksi.nomor_transaksi}")
                            print(f"Waktu         : {transaksi.waktu_transaksi.strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"Kasir         : {kasir.nama_lengkap}")
                            print(f"Pembeli       : {pembeli_aktif.nama_pembeli} ({pembeli_aktif.nik_tampil_masked or 'Umum'})")
                            print("-" * 50)
                            for d in transaksi.daftar_detail:
                                print(f"{d.barang.nama_barang} x{d.jumlah_beli} @Rp {d.harga_satuan_saat_transaksi} = Rp {d.subtotal}")
                            print("-" * 50)
                            print(f"Total Tagihan : Rp {transaksi.total_tagihan}")
                            print(f"Tunai Dibayar : Rp {pembayaran.nominal_dibayar}")
                            print(f"Kembalian     : Rp {pembayaran.nominal_kembalian}")
                            print("=" * 50)

                            cek_peringatan_stok_minimum(daftar_barang)
                            break
                        except ValueError as e:
                            print(f"[Gagal Pembayaran] {e}")

        elif pilih == "2":
            print("\n--- TAMBAH KUALIFIKASI KOMODITAS PEMBELI (FR-08) ---")
            if not daftar_pembeli:
                print("[Info] Belum ada pembeli terdaftar.")
                continue
            for idx, p in enumerate(daftar_pembeli):
                print(f" [{idx+1}] {p.nama_pembeli} | NIK: {p.nik_tampil_masked or '-'}")
            try:
                idx_p = int(input("Pilih nomor pembeli: ").strip()) - 1
                if 0 <= idx_p < len(daftar_pembeli):
                    p = daftar_pembeli[idx_p]
                    program_aktif = sorted({
                        b.aturan_penjualan.kode_program_komoditas
                        for b in daftar_barang
                        if b.aturan_penjualan and b.aturan_penjualan.status_aktif
                    })
                    if program_aktif:
                        print(f"Program komoditas terdaftar saat ini: {', '.join(program_aktif)}")
                    prog = input("Kode Program Komoditas: ").strip().upper()
                    kat_sasaran = input("Kategori Sasaran (mis. RUMAH_TANGGA / USAHA_MIKRO / PETANI_SASARAN / NELAYAN_SASARAN): ").strip().upper()
                    no_dok = input("Nomor Dokumen Pendukung (mis. No. KK / Kartu Tani): ").strip()
                    masa_hari = int(input("Masa berlaku dalam hari (mis. 365): ").strip())

                    kual = KualifikasiPembeli(
                        id_kualifikasi=f"KUAL-{datetime.now().strftime('%H%M%S')}",
                        kode_program_komoditas=prog,
                        kategori_sasaran=kat_sasaran,
                        nomor_dokumen_pendukung=no_dok or None,
                        status_verifikasi=True,
                        tanggal_berlaku_sampai=date.today() + timedelta(days=masa_hari)
                    )
                    p.tambah_kualifikasi_komoditas(kual)
                    print(f"[Sukses] Kualifikasi {prog} ({kat_sasaran}) ditambahkan untuk {p.nama_pembeli}.")
            except Exception as e:
                print(f"[Error] {e}")

        elif pilih == "3":
            print(f"\n--- RIWAYAT PENJUALAN KASIR: {kasir.nama_lengkap} ---")
            tx_saya = [tx for tx in daftar_transaksi if tx.kasir.id_user == kasir.id_user]
            if not tx_saya:
                print("[Info] Anda belum memproses transaksi apa pun.")
            for tx in tx_saya:
                print(f" - [{tx.nomor_transaksi}] {tx.waktu_transaksi.strftime('%Y-%m-%d %H:%M')} | "
                      f"Pembeli: {tx.pembeli.nama_pembeli} | Status: {tx.status_transaksi} | Total: Rp {tx.total_tagihan}")

        elif pilih == "4":
            kasir.logout()
            print("[Info] Logout dari akun Kasir.")
            break
        else:
            print("[Error] Pilihan tidak valid.")


# =====================================================================
# 5. MODUL ANTARMUKA PETUGAS GUDANG (FR-14 s.d. FR-17, MATRIKS O-18)
# =====================================================================

def menu_petugas_gudang(petugas: PetugasGudang, daftar_barang: list, daftar_supplier: list, daftar_aktivitas: list):
    while True:
        cek_peringatan_stok_minimum(daftar_barang)
        print("\n========================================================")
        print(f"  MENU PETUGAS GUDANG ({petugas.nama_lengkap})")
        print("========================================================")
        print("1. Catat Barang Masuk dari Supplier (FR-14)")
        print("2. Catat Barang Keluar Nonpenjualan (FR-15)")
        print("3. Penyesuaian Stok / Stock Opname (FR-16)")
        print("4. Lihat Semua Riwayat Aktivitas Persediaan (Baca Saja - FR-19)")
        print("5. Logout")
        pilih = input("Pilih menu (1-5): ").strip()

        if pilih in ("1", "2", "3"):
            if not daftar_barang:
                print("[Error] Master barang kosong.")
                continue
            print("\n--- PILIH BARANG ---")
            for idx, b in enumerate(daftar_barang):
                print(f" [{idx+1}] [{b.kode_barang}] {b.nama_barang} | Stok Saat Ini: {b.stok_tersedia} {b.satuan}")
            try:
                idx_b = int(input("Pilih nomor barang: ").strip()) - 1
                if not (0 <= idx_b < len(daftar_barang)):
                    print("[Error] Nomor barang tidak valid.")
                    continue
                brg = daftar_barang[idx_b]

                if pilih == "1":
                    print("\n--- FORM BARANG MASUK ---")
                    for i, s in enumerate(daftar_supplier):
                        print(f" [{i+1}] {s.nama_supplier} ({s.jenis_instansi})")
                    idx_s = int(input("Pilih nomor supplier: ").strip()) - 1
                    if not (0 <= idx_s < len(daftar_supplier)):
                        print("[Error] Supplier tidak valid.")
                        continue
                    sup = daftar_supplier[idx_s]
                    jml = int(input(f"Jumlah masuk ({brg.satuan}): ").strip())
                    no_sj = input("Nomor Surat Jalan (wajib diisi): ").strip()
                    harga_beli = Decimal(input("Harga beli satuan (Rp): ").strip())
                    ket = input("Catatan tambahan: ").strip()

                    akt = petugas.catat_barang_masuk(brg, sup, jml, no_sj, harga_beli, ket)
                    daftar_aktivitas.append(akt)
                    print(f"[Sukses] Barang masuk tercatat (ID: {akt.id_aktivitas}). Stok baru: {brg.stok_tersedia} {brg.satuan}.")

                elif pilih == "2":
                    print("\n--- FORM BARANG KELUAR NONPENJUALAN ---")
                    jml = int(input(f"Jumlah keluar ({brg.satuan}): ").strip())
                    keperluan = input("Keperluan (RUSAK / KEDALUWARSA / KEBUTUHAN_INTERNAL): ").strip().upper()
                    if keperluan not in ("RUSAK", "KEDALUWARSA", "KEBUTUHAN_INTERNAL"):
                        print("[Error] Jenis keperluan harus RUSAK, KEDALUWARSA, atau KEBUTUHAN_INTERNAL.")
                        continue
                    penerima = input("Nama penerima / penanggung jawab: ").strip()
                    ket = input("Catatan: ").strip()

                    akt = petugas.catat_barang_keluar(brg, jml, keperluan, penerima, ket)
                    daftar_aktivitas.append(akt)
                    print(f"[Sukses] Barang keluar tercatat (ID: {akt.id_aktivitas}). Stok baru: {brg.stok_tersedia} {brg.satuan}.")

                elif pilih == "3":
                    print("\n--- FORM STOCK OPNAME ---")
                    stok_fisik = int(input(f"Masukkan stok fisik hasil hitung aktual ({brg.satuan}): ").strip())
                    if stok_fisik == brg.stok_tersedia:
                        print("[Info] Stok fisik sama dengan stok sistem (selisih 0). Penyesuaian dibatalkan.")
                        continue
                    alasan = input("Alasan penyesuaian stok (wajib diisi): ").strip()
                    ket = input("Catatan tambahan: ").strip()

                    akt = petugas.catat_penyesuaian_stok(brg, stok_fisik, alasan, ket)
                    daftar_aktivitas.append(akt)
                    print(f"[Sukses] Stock opname tercatat (ID: {akt.id_aktivitas}). Selisih: {akt.selisih_stok:+d}. Stok akhir: {brg.stok_tersedia}.")

            except Exception as e:
                print(f"[Error] {e}")

        elif pilih == "4":
            print("\n--- RIWAYAT AKTIVITAS PERSEDIAAN (BACA SAJA) ---")
            if not daftar_aktivitas:
                print("[Info] Belum ada riwayat mutasi gudang.")
            for akt in daftar_aktivitas:
                r = akt.dapatkan_ringkasan_audit()
                print(f" - [{r['id_aktivitas']}] {r['waktu_aktivitas'][:19]} | {akt.__class__.__name__} | "
                      f"{r['nama_barang']} | {r['stok_sebelum']} -> {r['stok_sesudah']} ({r['jumlah_perubahan']:+d}) | "
                      f"Petugas: {r['nama_petugas']} | Ket: {r['catatan']}")

        elif pilih == "5":
            petugas.logout()
            print("[Info] Logout dari akun Petugas Gudang.")
            break
        else:
            print("[Error] Pilihan tidak valid.")


# =====================================================================
# 6. GERBANG UTAMA APLIKASI CLI (MAIN LOOP)
# =====================================================================

def main():
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


if __name__ == "__main__":
    main()