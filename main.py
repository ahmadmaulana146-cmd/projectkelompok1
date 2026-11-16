from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
import sys
from unittest.mock import patch

from models.pengguna.admin import Admin
from models.pengguna.kasir import Kasir
from models.pengguna.petugas_gudang import PetugasGudang
from models.inventaris.kategori import Kategori
from models.inventaris.supplier import Supplier
from models.inventaris.barang import Barang
from models.pembeli.pembeli import Pembeli
from models.pembeli.kualifikasi_pembeli import KualifikasiPembeli
from models.pembeli.aturan_penjualan import AturanPenjualan
from models.transaksi.transaksi_penjualan import TransaksiPenjualan
from models.transaksi.detail_transaksi import DetailTransaksi
from models.transaksi.pembayaran import Pembayaran
from models.transaksi.layanan_laporan import LayananLaporan
from models.persediaan.barang_masuk import BarangMasuk
from models.persediaan.barang_keluar import BarangKeluar
from models.persediaan.penyesuaian_stok import PenyesuaianStok


def setup_initial_data():
    """Inisialisasi data master awal sesuai arsitektur domain SIMIP."""
    kategori = Kategori("KAT-01", "Sembako Bersubsidi", "Bahan pokok program pemerintah")
    supplier = Supplier("SUP-01", "PT Pangan Desa Sejahtera", "Distributor Utama", "08123456789", "Jakarta")
    
    aturan = AturanPenjualan(
        id_aturan="ATR-01",
        kode_program_komoditas="SUBSIDI-BERAS-2026",
        harga_eceran_tertinggi=Decimal("12500"),
        batas_maksimal_per_transaksi=5,
        batas_maksimal_per_periode=10,
        periode_kuota="BULANAN",
        wajib_identitas_nik=True,
        daftar_kategori_pembeli_diizinkan=["KURANG_MAMPU"],
        status_aktif=True
    )

    barang = Barang(
        kode_barang="BRG-001",
        nama_barang="Beras Premium 5kg",
        satuan="Karung",
        harga_dasar=Decimal("14000"),
        stok_tersedia=25,
        stok_minimum=5,
        status_aktif=True,
        kategori=kategori,
        aturan_penjualan=aturan
    )

    users = {
        "admin": Admin("U-01", "admin", Admin.hash_password("admin123"), "Administrator Pusat"),
        "kasir": Kasir("U-02", "kasir", Kasir.hash_password("kasir123"), "Budi Kasir", "Pagi"),
        "gudang": PetugasGudang("U-03", "gudang", PetugasGudang.hash_password("gudang123"), "Siti Gudang")
    }

    daftar_barang = [barang]
    daftar_supplier = [supplier]
    daftar_kategori = [kategori]
    daftar_transaksi = []
    daftar_aktivitas = []
    daftar_pembeli = []

    return users, daftar_barang, daftar_supplier, daftar_kategori, daftar_transaksi, daftar_aktivitas, daftar_pembeli


def menu_admin(admin: Admin, daftar_barang, daftar_kategori, daftar_supplier, daftar_transaksi, daftar_aktivitas):
    """Antarmuka Menu Interaktif untuk Admin."""
    while True:
        print("\n=== MENU ADMIN ===")
        print("1. Kelola & Lihat Daftar Barang")
        print("2. Atur Harga & Ketentuan Komoditas (Aturan Penjualan / HET)")
        print("3. Lihat Laporan Penjualan & Persediaan")
        print("4. Logout")
        pilihan = input("Pilih menu (1-4): ").strip()

        if pilihan == "1":
            print(f"\n   [Info] Total Barang terdaftar: {len(daftar_barang)}")
            for b in daftar_barang:
                print(f"   - [{b.kode_barang}] {b.nama_barang} | Stok: {b.stok_tersedia} {b.satuan} | Harga Dasar: Rp {b.harga_dasar} | HET: Rp {b.dapatkan_harga_berlaku()}")
        elif pilihan == "2":
            if daftar_barang:
                b = daftar_barang[0]
                print(f"\n   [Keterangan Barang Terpilih]")
                print(f"   Nama Barang : {b.nama_barang}")
                print(f"   HET Saat Ini: Rp {b.dapatkan_harga_berlaku()}")
                try:
                    het_baru = Decimal(input("   Masukkan Harga Eceran Tertinggi (HET) baru (Rp): ").strip())
                    if b.aturan_penjualan:
                        b.aturan_penjualan.harga_eceran_tertinggi = het_baru
                        print("   [Sukses] HET berhasil diperbarui!")
                    else:
                        print("   [Info] Barang ini tidak memiliki aturan penjualan aktif.")
                except Exception as e:
                    print(f"   [Error] Gagal mengubah HET: {e}")
        elif pilihan == "3":
            svc = LayananLaporan(daftar_transaksi, daftar_barang, daftar_aktivitas)
            laporan = svc.hasilkan_laporan_penjualan(date(2026, 1, 1), date(2026, 12, 31))
            print("\n   --- LAPORAN PENJUALAN ---")
            print(f"   Total Transaksi Selesai : {laporan['jumlah_transaksi']}")
            print(f"   Total Omset             : Rp {laporan['total_omset']}")
            print("\n   --- LAPORAN PERSEDIAAN ---")
            for st in svc.hasilkan_laporan_persediaan(False):
                print(f"   - {st['nama_barang']}: Stok={st['stok_tersedia']} {st['satuan']} (Kritis: {st['status_kritis']})")
        elif pilihan == "4":
            print("   Logout dari akun Admin.")
            break
        else:
            print("   Pilihan tidak valid.")


def menu_kasir(kasir: Kasir, daftar_barang, daftar_pembeli, daftar_transaksi):
    """Antarmuka Menu Interaktif untuk Kasir."""
    while True:
        print("\n=== MENU KASIR (TRANSAKSI PENJUALAN) ===")
        print("1. Buat Transaksi Penjualan Baru")
        print("2. Logout")
        pilih = input("Pilih menu (1-2): ").strip()

        if pilih == "1":
            print("\n--- Catat Identitas Pembeli ---")
            nama_cust = input("Nama Pembeli: ").strip()
            nik_cust = input("NIK Pembeli (kosongkan jika umum): ").strip()
            nik_val = nik_cust if nik_cust else None
            alamat_cust = input("Alamat Domisili: ").strip()

            pembeli = kasir.catat_data_pembeli(nama=nama_cust, nik=nik_val, alamat=alamat_cust)
            if nik_val:
                kual = KualifikasiPembeli(
                    id_kualifikasi=f"KUAL-{datetime.now().strftime('%H%M%S')}",
                    kode_program_komoditas="SUBSIDI-BERAS-2026",
                    kategori_sasaran="KURANG_MAMPU",
                    status_verifikasi=True
                )
                pembeli.tambah_kualifikasi_komoditas(kual)
                print("   [Info] Kualifikasi subsidi 'KURANG_MAMPU' otomatis dilampirkan untuk NIK ini.")

            daftar_pembeli.append(pembeli)
            transaksi = kasir.buat_transaksi_baru(pembeli=pembeli)
            print(f"   [Sukses] Transaksi dibuat dengan No: {transaksi.nomor_transaksi}")

            while True:
                print("\n   Daftar Barang Tersedia:")
                for idx, b in enumerate(daftar_barang):
                    print(f"   [{idx+1}] {b.nama_barang} (Stok: {b.stok_tersedia} {b.satuan}, Harga HET: Rp {b.dapatkan_harga_berlaku()})")
                
                pilih_brg = input("   Pilih nomor barang (atau ketik 'selesai'): ").strip()
                if pilih_brg.lower() == 'selesai':
                    break
                
                try:
                    idx_b = int(pilih_brg) - 1
                    if 0 <= idx_b < len(daftar_barang):
                        barang_pilih = daftar_barang[idx_b]
                        
                        print(f"\n   [Keterangan Barang Dipilih]")
                        print(f"   - Nama Barang   : {barang_pilih.nama_barang}")
                        print(f"   - Satuan        : {barang_pilih.satuan}")
                        print(f"   - Stok Tersedia : {barang_pilih.stok_tersedia}")
                        
                        jumlah_beli = int(input(f"   Masukkan jumlah yang dibeli ({barang_pilih.satuan}): ").strip())

                        hasil = transaksi.tambah_item_barang(barang=barang_pilih, jumlah=jumlah_beli)
                        if hasil.apakah_lolos():
                            print(f"   [Berhasil] {hasil.pesan_validasi}")
                            print(f"   Subtotal Tagihan Sementara: Rp {transaksi.total_tagihan}")
                        else:
                            print(f"   [DITOLAK] {hasil.pesan_validasi}")
                    else:
                        print("   Nomor barang tidak valid.")
                except ValueError as e:
                    print(f"   [Error] Masukkan angka yang valid: {e}")

            if len(transaksi.daftar_detail) > 0:
                print(f"\n   Total Tagihan Keseluruhan: Rp {transaksi.total_tagihan}")
                while True:
                    try:
                        bayar_str = input("   Masukkan nominal uang tunai yang dibayar (Rp): ").strip()
                        nominal_bayar = Decimal(bayar_str)
                        
                        pembayaran = transaksi.proses_pembayaran(nominal_bayar=nominal_bayar, metode="TUNAI")
                        print(f"   [Pembayaran Sukses] Kembalian: Rp {pembayaran.nominal_kembalian}")
                        
                        transaksi.selesaikan_transaksi()
                        daftar_transaksi.append(transaksi)
                        print("   [Sukses] Transaksi selesai! Stok persediaan telah dikurangi secara atomik.")
                        break
                    except ValueError as e:
                        print(f"   [Gagal Pembayaran] {e}")
                        opsi = input("   Coba ulangi pembayaran? (y/n): ").strip().lower()
                        if opsi != 'y':
                            transaksi.batalkan_transaksi("Pembayaran dibatalkan oleh kasir.")
                            print("   [Info] Transaksi dibatalkan.")
                            break
            else:
                print("   [Info] Keranjang belanja kosong, transaksi dibatalkan.")
        elif pilih == "2":
            print("   Logout dari akun Kasir.")
            break
        else:
            print("   Pilihan tidak valid.")


def menu_petugas_gudang(petugas: PetugasGudang, daftar_barang, daftar_supplier, daftar_aktivitas):
    """Antarmuka Menu Interaktif untuk Petugas Gudang."""
    while True:
        print("\n=== MENU PETUGAS GUDANG (AKTIVITAS PERSEDIAAN) ===")
        print("1. Barang Masuk (Restock Stok)")
        print("2. Barang Keluar (Rusak / Expired / Internal)")
        print("3. Penyesuaian Stok (Stock Opname)")
        print("4. Logout")
        pilih = input("Pilih menu (1-4): ").strip()

        if daftar_barang:
            barang = daftar_barang[0]
        else:
            print("   [Error] Belum ada barang di dalam sistem.")
            continue

        print(f"\n   [Keterangan Barang Aktif]")
        print(f"   - Nama Barang   : {barang.nama_barang}")
        print(f"   - Stok Saat Ini : {barang.stok_tersedia} {barang.satuan}")

        if pilih == "1":
            print("\n   --- Pencatatan Barang Masuk ---")
            try:
                jml = int(input(f"   Masukkan jumlah barang masuk ({barang.satuan}): ").strip())
                no_ref = input("   Masukkan Nomor Referensi / Surat Jalan: ").strip()
                harga_beli = Decimal(input("   Masukkan harga beli satuan (Rp): ").strip())
                ket = input("   Masukkan catatan tambahan: ").strip()

                supplier = daftar_supplier[0]
                aktivitas = petugas.catat_barang_masuk(
                    barang=barang, supplier=supplier, jumlah=jml,
                    no_ref=no_ref, harga_beli=harga_beli, ket=ket
                )
                daftar_aktivitas.append(aktivitas)
                print(f"   [Sukses] Barang masuk dicatat. Stok terkini: {barang.stok_tersedia}")
            except Exception as e:
                print(f"   [Error] {e}")
        elif pilih == "2":
            print("\n   --- Pencatatan Barang Keluar ---")
            try:
                jml = int(input(f"   Masukkan jumlah barang keluar ({barang.satuan}): ").strip())
                tujuan = input("   Masukkan jenis keperluan keluar (rusak/expired/internal): ").strip()
                penerima = input("   Masukkan nama penerima internal: ").strip()
                ket = input("   Masukkan catatan: ").strip()

                aktivitas = petugas.catat_barang_keluar(
                    barang=barang, jumlah=jml, tujuan=tujuan, penerima=penerima, ket=ket
                )
                daftar_aktivitas.append(aktivitas)
                print(f"   [Sukses] Barang keluar dicatat. Stok terkini: {barang.stok_tersedia}")
            except Exception as e:
                print(f"   [Error] {e}")
        elif pilih == "3":
            print("\n   --- Pencatatan Penyesuaian Stok (Stock Opname) ---")
            try:
                stok_fisik = int(input(f"   Masukkan hasil penghitungan stok fisik aktual ({barang.satuan}): ").strip())
                alasan = input("   Masukkan alasan penyesuaian wajib diisi: ").strip()
                ket = input("   Masukkan catatan tambahan: ").strip()

                aktivitas = petugas.catat_penyesuaian_stok(
                    barang=barang, stok_fisik=stok_fisik, alasan=alasan, ket=ket
                )
                daftar_aktivitas.append(aktivitas)
                print(f"   [Sukses] Stock opname dicatat. Selisih: {aktivitas.selisih_stok}. Stok Akhir: {barang.stok_tersedia}")
            except Exception as e:
                print(f"\n   [Error] {e}")
        elif pilih == "4":
            print("   Logout dari Petugas Gudang.")
            break
        else:
            print("   Pilihan tidak valid.")


def jalankan_simulasi_otomatis_interaktif():
    """Menjalankan simulasi otomatis dengan mensimulasikan input pengguna secara nyata."""
    print("==================================================================")
    print("  SIMULASI OTOMATIS (MENSIMULASIKAN USER INPUT SECARA OTOMATIS)    ")
    print("==================================================================")
    
    simulated_inputs = [
        "1", 
        "admin", "admin123",
        "1",
        "2", "12000",
        "3",
        "4",
        "gudang", "gudang123",
        "1", "20", "SJ-2026-001", "11000", "Barang masuk",
        "2", "2", "rusak", "Display", "Rusak kemasan",
        "3", "40", "Opname bulanan", "Stock opname fisik",
        "4",
        "kasir", "kasir123",
        "1",
        "Siti Rahma", "3201123456780009", "Jl. Mawar No. 12",
        "1",
        "6",
        "3",
        "selesai",
        "50000",
        "2",
        "menu",
        "3",
        ""
    ]

    def mock_input(prompt=''):
        print(prompt, end='')
        if simulated_inputs:
            val = simulated_inputs.pop(0)
            print(val)
            return val
        return ""

    with patch('builtins.input', side_effect=mock_input):
        try:
            main_loop_core()
        except Exception as e:
            print(f"\n[Info] Simulasi otomatis selesai menjalankan seluruh skenario user.")


def main_loop_core():
    users, daftar_barang, daftar_supplier, daftar_kategori, daftar_transaksi, daftar_aktivitas, daftar_pembeli = setup_initial_data()
    
    while True:
        print("\n=====================================================")
        print("  APLIKASI KOPERASI DESA MERAH PUTIH (SIMIP) - OOP   ")
        print("=====================================================")
        print("Pilih mode jalankan aplikasi:")
        print("  [1] Mode Interaktif (Manual mengetik di terminal)")
        print("  [2] Mode Otomatis (Mensimulasikan user input otomatis)")
        print("  [3] Keluar dari Aplikasi")
        
        mode = input("Pilih mode (1-3): ").strip()

        if mode == "3" or mode.lower() == 'keluar':
            print("Terima kasih telah menggunakan sistem SIMIP!")
            break
        elif mode == "2":
            jalankan_simulasi_otomatis_interaktif()
            input("\n[Selesai] Tekan Enter untuk kembali ke menu utama...")
            break
        elif mode == "1":
            print("\n=====================================================")
            print("  MASUK KE MODE INTERAKTIF")
            print("=====================================================")
            print("Akun Demo yang tersedia:")
            print(" - Admin  : username='admin', password='admin123'")
            print(" - Kasir  : username='kasir', password='kasir123'")
            print(" - Gudang : username='gudang', password='gudang123'")
            print("=====================================================")

            while True:
                print("\n--- FORM LOGIN PENGGUNA ---")
                u_input = input("Username (atau ketik 'menu' untuk kembali): ").strip()
                if u_input.lower() == 'menu':
                    break
                if u_input.lower() == 'keluar':
                    print("Terima kasih!")
                    sys.exit(0)

                p_input = input("Password: ").strip()

                user_obj = users.get(u_input)
                if user_obj and user_obj.login(u_input, p_input):
                    print(f"   [Login Berhasil] Selamat datang, {user_obj.nama_lengkap}!")
                    print(f"   [Identifikasi Peran] Peran terdeteksi: {user_obj.peran}")

                    if isinstance(user_obj, Admin):
                        menu_admin(user_obj, daftar_barang, daftar_kategori, daftar_supplier, daftar_transaksi, daftar_aktivitas)
                    elif isinstance(user_obj, Kasir):
                        menu_kasir(user_obj, daftar_barang, daftar_pembeli, daftar_transaksi)
                    elif isinstance(user_obj, PetugasGudang):
                        menu_petugas_gudang(user_obj, daftar_barang, daftar_supplier, daftar_aktivitas)
                else:
                    print("   [Login Gagal] Kredensial tidak valid atau akun non-aktif.")
        else:
            print("   [Pilihan tidak valid] Silakan masukkan angka 1, 2, atau 3.")


def main():
    main_loop_core()


if __name__ == "__main__":
    main()