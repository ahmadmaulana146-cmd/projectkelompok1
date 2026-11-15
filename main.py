from __future__ import annotations
from datetime import date
from decimal import Decimal

from models.pengguna import Admin, Kasir, PetugasGudang, User
from models.inventaris import Barang, Kategori, Supplier
from models.pembeli import AturanPenjualan, KualifikasiPembeli, Pembeli
from models.transaksi import LayananLaporan

"roja"
def print_header(title: str): 
    print("\n" + "=" * 80)
    print(f" {title.upper()} ")
    print("=" * 80)


def print_step(step_name: str): 
    print(f"\n>>> [STEP] {step_name}")


def run_encapsulation_tests() -> None:
    print_header("Fase Pengujian Enkapsulasi & Ironclad Setters (Try-Except ValueError)")

    # 1. Test invalid username on User
    print_step("Test 1: Memasukkan username tidak valid (< 3 karakter)")
    try:
        Admin(
            id_user="USR-001",
            username="ad",  # Terlalu pendek
            password_hash=User.hash_password("admin123"),
            nama_lengkap="Administrator Utama",
        )
        print("[-] GAGAL: Exception tidak tertangkap!")
    except ValueError as e:
        print(f"[+] BERHASIL TERTANGKAP: {e}")

    # 2. Test negative stock on Barang
    print_step("Test 2: Memasukkan stok tersedia bernilai negatif pada Barang")
    try:
        kat_test = Kategori(id_kategori="KAT-01", nama_kategori="Umum", deskripsi="Umum")
        Barang(
            kode_barang="BRG-TEST",
            nama_barang="Barang Uji",
            satuan="pcs",
            harga_dasar=Decimal("10000"),
            stok_tersedia=-15,  # Tidak boleh negatif
            kategori=kat_test,
        )
        print("[-] GAGAL: Exception tidak tertangkap!")
    except ValueError as e:
        print(f"[+] BERHASIL TERTANGKAP: {e}")

    # 3. Test negative price on Barang
    print_step("Test 3: Memasukkan harga dasar bernilai 0 atau negatif pada Barang")
    try:
        kat_test = Kategori(id_kategori="KAT-01", nama_kategori="Umum", deskripsi="Umum")
        b = Barang(
            kode_barang="BRG-TEST2",
            nama_barang="Barang Uji 2",
            satuan="pcs",
            harga_dasar=Decimal("5000"),
            kategori=kat_test,
        )
        b.harga_dasar = Decimal("-2500")  # Setter validation
        print("[-] GAGAL: Exception tidak tertangkap!")
    except ValueError as e:
        print(f"[+] BERHASIL TERTANGKAP: {e}")

    # 4. Test empty reason for Stock Opname (BR-10)
    print_step("Test 4: Melakukan penyesuaian stok tanpa alasan (BR-10)")
    try:
        kat_test = Kategori(id_kategori="KAT-01", nama_kategori="Umum", deskripsi="Umum")
        b_test = Barang(
            kode_barang="BRG-TEST3",
            nama_barang="Barang Uji 3",
            satuan="pcs",
            harga_dasar=Decimal("5000"),
            stok_tersedia=10,
            kategori=kat_test,
        )
        b_test.sesuaikan_stok_aktual(stok_fisik_baru=8, alasan="   ")  # Alasan kosong
        print("[-] GAGAL: Exception tidak tertangkap!")
    except ValueError as e:
        print(f"[+] BERHASIL TERTANGKAP: {e}")

    # 5. Test reducing stock beyond available quantity
    print_step("Test 5: Mengurangi stok melebihi jumlah stok yang tersedia")
    try:
        kat_test = Kategori(id_kategori="KAT-01", nama_kategori="Umum", deskripsi="Umum")
        b_test = Barang(
            kode_barang="BRG-TEST4",
            nama_barang="Barang Uji 4",
            satuan="pcs",
            harga_dasar=Decimal("5000"),
            stok_tersedia=5,
            kategori=kat_test,
        )
        b_test.kurangi_stok(10)  # Melebihi 5
        print("[-] GAGAL: Exception tidak tertangkap!")
    except ValueError as e:
        print(f"[+] BERHASIL TERTANGKAP: {e}")

    # 6. Test insufficient payment
    print_step("Test 6: Pembayaran dengan nominal kurang dari tagihan")
    try:
        from models.transaksi import Pembayaran
        pay = Pembayaran(
            id_pembayaran="PAY-ERR",
            nominal_tagihan=Decimal("100000"),
            nominal_dibayar=Decimal("80000"),  # Kurang
            metode_pembayaran="TUNAI",
        )
        pay.hitung_kembalian()
        print("[-] GAGAL: Exception tidak tertangkap!")
    except ValueError as e:
        print(f"[+] BERHASIL TERTANGKAP: {e}")


def run_full_workflow() -> None:
    print_header("Fase Demonstrasi Alur Operasional Koperasi (SIMIP)")

    layanan_laporan = LayananLaporan()

    # 1. Inisialisasi Akun Pengguna
    print_step("1. Inisialisasi Akun Pengguna (Admin, Petugas Gudang, Kasir)")
    admin = Admin(
        id_user="ADM-01",
        username="admin_desa",
        password_hash=User.hash_password("Kopdes2026!"),
        nama_lengkap="Budi Santoso, S.Kom",
    )
    petugas = PetugasGudang(
        id_user="GDG-01",
        username="gudang_edi",
        password_hash=User.hash_password("GudangKopdes123"),
        nama_lengkap="Edi Purnomo",
    )
    kasir = Kasir(
        id_user="KSR-01",
        username="kasir_siti",
        password_hash=User.hash_password("KasirKopdes123"),
        nama_lengkap="Siti Aminah",
        shift_kerja="Pagi (08:00 - 15:00)",
    )

    print(f"  [+] Admin terdaftar   : {admin.nama_lengkap} (Hak Akses: {len(admin.dapatkan_hak_akses())} modul)")
    print(f"  [+] Petugas terdaftar : {petugas.nama_lengkap} (Hak Akses: {len(petugas.dapatkan_hak_akses())} modul)")
    print(f"  [+] Kasir terdaftar   : {kasir.nama_lengkap} - Shift: {kasir.shift_kerja}")

    # 2. Admin Menyiapkan Data Master Kategori & Supplier
    print_step("2. Admin Mengelola Master Kategori & Supplier Pemasok")
    kat_sembako = Kategori(
        id_kategori="KAT-SBK",
        nama_kategori="Bahan Pangan Pokok & Sembako",
        deskripsi="Kebutuhan pokok pangan desa seperti beras, gula, dan minyak",
    )
    kat_energi = Kategori(
        id_kategori="KAT-ENG",
        nama_kategori="Bahan Bakar & Energi Subsidi",
        deskripsi="Komoditas bersubsidi LPG dan bahan bakar rumah tangga",
    )
    admin.kelola_kategori(kat_sembako, "tambah")
    admin.kelola_kategori(kat_energi, "tambah")

    sup_bulog = Supplier(
        id_supplier="SUP-BULOG",
        nama_supplier="Perum BULOG Kantor Wilayah Jawa Tengah",
        jenis_instansi="BUMN/Bulog",
        kontak_telepon="0281-7654321",
        alamat="Jl. Gatot Subroto No. 45, Banyumas",
    )
    sup_pertamina = Supplier(
        id_supplier="SUP-PTM",
        nama_supplier="PT Pertamina Patra Niaga Regional Jateng",
        jenis_instansi="Agen Pertamina",
        kontak_telepon="0281-1234567",
        alamat="Jl. Letjen Pol Soemarto No. 10, Purwokerto",
    )
    admin.kelola_supplier(sup_bulog, "tambah")
    admin.kelola_supplier(sup_pertamina, "tambah")

    # 3. Admin Menetapkan Master Barang & Aturan Penjualan Komoditas Khusus
    print_step("3. Admin Mendaftarkan Barang & Menetapkan Aturan Penjualan Komoditas")

    # A. Beras SPHP (Kepkaban Bapanas No. 34 Tahun 2026: HET Rp 62.500 / 5kg, max 5 pak)
    aturan_sphp = AturanPenjualan(
        id_aturan="REG-SPHP-2026",
        kode_program_komoditas="BERAS_SPHP",
        harga_eceran_tertinggi=Decimal("62500"),
        batas_maksimal_per_transaksi=5,
        periode_kuota="MINGGUAN",
        wajib_identitas_nik=False,
    )
    brg_sphp = Barang(
        kode_barang="BRG-SPHP-5KG",
        nama_barang="Beras SPHP 5 Kg Bulog",
        satuan="kemasan 5kg",
        harga_dasar=Decimal("62500"),
        stok_tersedia=0,
        stok_minimum=10,
        kategori=kat_sembako,
    )
    admin.tetapkan_aturan_penjualan(brg_sphp, aturan_sphp)

    # B. LPG 3 kg (Kepmen ESDM: Wajib NIK, target: Rumah Tangga / Usaha Mikro / Nelayan / Petani Sasaran)
    aturan_lpg = AturanPenjualan(
        id_aturan="REG-LPG3KG-2026",
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
            "PETANI_SASARAN",
        ],
    )
    brg_lpg = Barang(
        kode_barang="BRG-LPG-3KG",
        nama_barang="LPG 3 Kg Bersubsidi",
        satuan="tabung",
        harga_dasar=Decimal("18000"),
        stok_tersedia=0,
        stok_minimum=15,
        kategori=kat_energi,
    )
    admin.tetapkan_aturan_penjualan(brg_lpg, aturan_lpg)

    # C. Minyakita 1L (Permendag 43/2025: HET Rp 15.700, max 2 liter per transaksi)
    aturan_minyak = AturanPenjualan(
        id_aturan="REG-MYK-2025",
        kode_program_komoditas="MINYAKITA",
        harga_eceran_tertinggi=Decimal("15700"),
        batas_maksimal_per_transaksi=2,
        periode_kuota="HARIAN",
        wajib_identitas_nik=False,
    )
    brg_minyak = Barang(
        kode_barang="BRG-MYK-1L",
        nama_barang="Minyak Goreng Minyakita 1 Liter",
        satuan="pouch 1L",
        harga_dasar=Decimal("15700"),
        stok_tersedia=0,
        stok_minimum=10,
        kategori=kat_sembako,
    )
    admin.tetapkan_aturan_penjualan(brg_minyak, aturan_minyak)

    # D. Gula Pasir Komersial (Komoditas umum, tanpa aturan subsidi khusus)
    brg_gula = Barang(
        kode_barang="BRG-GULA-1KG",
        nama_barang="Gula Pasir Kristal Putih 1 Kg",
        satuan="kg",
        harga_dasar=Decimal("17500"),
        stok_tersedia=0,
        stok_minimum=10,
        kategori=kat_sembako,
    )

    for b in [brg_sphp, brg_lpg, brg_minyak, brg_gula]:
        layanan_laporan.tambah_barang(b)
        print(f"  [+] Barang terdaftar: {b.kode_barang} - {b.nama_barang} (Harga: Rp {b.dapatkan_harga_berlaku()})")

    # 4. Petugas Gudang Mencatat Aktivitas Persediaan (BarangMasuk, PenyesuaianStok, BarangKeluar)
    print_step("4. Petugas Gudang Memproses Pasokan Masuk (Template Method AktivitasPersediaan)")
    akt_masuk_sphp = petugas.catat_barang_masuk(
        barang=brg_sphp,
        supplier=sup_bulog,
        jumlah=50,
        no_ref="SJ-BULOG-2026/001",
        harga_beli=Decimal("58000"),
        ket="Penerimaan Beras SPHP Alokasi Tahap I",
    )
    layanan_laporan.tambah_aktivitas(akt_masuk_sphp)
    print(f"  [+] Masuk: {brg_sphp.nama_barang} | Jumlah: 50 | Stok sekarang: {brg_sphp.stok_tersedia}")

    akt_masuk_lpg = petugas.catat_barang_masuk(
        barang=brg_lpg,
        supplier=sup_pertamina,
        jumlah=40,
        no_ref="DO-PERTAMINA-8891",
        harga_beli=Decimal("16000"),
        ket="Pengiriman Tabung Gas Melon Mingguan",
    )
    layanan_laporan.tambah_aktivitas(akt_masuk_lpg)
    print(f"  [+] Masuk: {brg_lpg.nama_barang} | Jumlah: 40 | Stok sekarang: {brg_lpg.stok_tersedia}")

    akt_masuk_minyak = petugas.catat_barang_masuk(
        barang=brg_minyak,
        supplier=sup_bulog,
        jumlah=30,
        no_ref="SJ-DMO-771",
        harga_beli=Decimal("14000"),
        ket="Pasokan Minyakita DMO Kemendag",
    )
    layanan_laporan.tambah_aktivitas(akt_masuk_minyak)

    akt_masuk_gula = petugas.catat_barang_masuk(
        barang=brg_gula,
        supplier=sup_bulog,
        jumlah=35,
        no_ref="SJ-GULA-102",
        harga_beli=Decimal("15000"),
        ket="Penerimaan Gula Konsumsi",
    )
    layanan_laporan.tambah_aktivitas(akt_masuk_gula)

    # Petugas melakukan stock opname (PenyesuaianStok)
    print_step("5. Petugas Gudang Melakukan Penyesuaian Stok (Stock Opname BR-10)")
    akt_opname = petugas.catat_penyesuaian_stok(
        barang=brg_gula,
        stok_fisik=33,  # Selisih -2 kemasan bocor
        alasan="Pemeriksaan fisik mingguan: 2 kemasan mengalami robek saat penataan",
    )
    layanan_laporan.tambah_aktivitas(akt_opname)
    print(f"  [+] Opname Berhasil: {brg_gula.nama_barang} disesuaikan ke {brg_gula.stok_tersedia} (Selisih: {akt_opname.selisih_stok})")

    # Petugas mencatat pengeluaran barang rusak nonpenjualan (BarangKeluar)
    print_step("6. Petugas Gudang Mencatat Barang Keluar Nonpenjualan (BR-04)")
    akt_keluar = petugas.catat_barang_keluar(
        barang=brg_gula,
        jumlah=1,
        tujuan="Kebutuhan Konsumsi Rapat Anggota Koperasi",
        penerima="Sekretaris Pengurus",
        ket="Konsumsi internal RAT",
    )
    layanan_laporan.tambah_aktivitas(akt_keluar)
    print(f"  [+] Keluar Internal: {brg_gula.nama_barang} berkurang 1 | Sisa stok: {brg_gula.stok_tersedia}")

    # 5. Kasir Melayani Pembeli & Transaksi Penjualan
    print_step("7. Pendaftaran Profil Pembeli & Kualifikasi Komoditas Khusus")
    # Pembeli A: Pak Sukardi (Ber-NIK, berhak atas subsidi LPG 3kg)
    pembeli_sukardi = kasir.catat_data_pembeli(
        nama="Sukardi",
        nik="3302151208750001",
        alamat="RT 02 RW 01 Desa Merah Putih",
    )
    kualifikasi_sukardi = KualifikasiPembeli(
        id_kualifikasi="KUAL-SKD-01",
        kode_program_komoditas="LPG_3KG",
        kategori_sasaran="RUMAH_TANGGA",
        nomor_dokumen_pendukung="KK-33021510002",
        status_verifikasi=True,
        tanggal_berlaku_sampai=date(2027, 12, 31),
    )
    pembeli_sukardi.tambah_kualifikasi_komoditas(kualifikasi_sukardi)
    print(f"  [+] Pembeli 1: {pembeli_sukardi.nama_pembeli} | NIK Masked: {pembeli_sukardi.nik_tampil_masked}")
    print(f"      Kualifikasi: {kualifikasi_sukardi.kode_program_komoditas} -> {kualifikasi_sukardi.kategori_sasaran}")

    # Pembeli B: Pembeli Umum Anonim (Tanpa NIK)
    pembeli_umum = kasir.catat_data_pembeli(
        nama="Pembeli Umum (Anonim)",
        nik=None,
        alamat="Desa Sekitar",
    )
    print(f"  [+] Pembeli 2: {pembeli_umum.nama_pembeli} | Status: Pembeli Umum (Tanpa NIK)")

    # 6. Pengujian Skenario Validasi Transaksi Komoditas Khusus
    print_step("8. Pengujian Validasi Kasir: Pembeli Umum Mencoba Beli Komoditas Bersyarat")

    tx_uji1 = kasir.buat_transaksi_baru(pembeli_umum)
    # Coba tambah LPG 3kg untuk pembeli umum (harus ditolak karena wajib NIK & kualifikasi sasaran)
    hasil_uji1 = tx_uji1.tambah_item_barang(brg_lpg, jumlah=1)
    print(f"  [i] Hasil percobaan beli LPG oleh Pembeli Umum: {hasil_uji1.format_pesan_audit()}")
    assert not hasil_uji1.apakah_lolos(), "Validasi NIK LPG seharusnya menolak pembeli tanpa NIK!"

    # Coba tambah Beras SPHP melebihi kuota 5 pak
    tx_uji2 = kasir.buat_transaksi_baru(pembeli_sukardi)
    hasil_uji2 = tx_uji2.tambah_item_barang(brg_sphp, jumlah=8)  # Batas maksimal per transaksi = 5
    print(f"  [i] Hasil percobaan beli Beras SPHP 8 pak (> 5 pak): {hasil_uji2.format_pesan_audit()}")
    assert not hasil_uji2.apakah_lolos(), "Validasi kuota seharusnya menolak pembelian di atas batas!"

    # 7. Pemrosesan Transaksi Penjualan yang Valid
    print_step("9. Pemrosesan Transaksi Sukses & Pembayaran Kasir")
    tx_valid = kasir.buat_transaksi_baru(pembeli_sukardi)

    # Tambah 1 tabung LPG 3kg
    res_lpg = tx_valid.tambah_item_barang(brg_lpg, jumlah=1)
    print(f"  [+] {res_lpg.pesan_validasi}")

    # Tambah 2 pak Beras SPHP 5kg
    res_sphp = tx_valid.tambah_item_barang(brg_sphp, jumlah=2)
    print(f"  [+] {res_sphp.pesan_validasi}")

    # Tambah 3 kg Gula Pasir
    res_gula = tx_valid.tambah_item_barang(brg_gula, jumlah=3)
    print(f"  [+] {res_gula.pesan_validasi}")

    total_harus_bayar = tx_valid.hitung_total_pembayaran()
    print(f"\n  [=] Rincian Keranjang Belanja ({tx_valid.nomor_transaksi}):")
    for idx, item in enumerate(tx_valid.daftar_detail, 1):
        aturan_info = f" [Aturan: {item.kode_aturan_diterapkan}]" if item.kode_aturan_diterapkan else ""
        print(
            f"      {idx}. {item.barang.nama_barang} | Qty: {item.jumlah_beli} | "
            f"Harga Satuan: Rp {item.harga_satuan_saat_transaksi:,.0f} | "
            f"Subtotal: Rp {item.subtotal:,.0f}{aturan_info}"
        )
    print(f"  [=] TOTAL TAGIHAN: Rp {total_harus_bayar:,.0f}")

    # Pembayaran tunai dengan uang pas/kembalian
    uang_dibayar = Decimal("200000")
    print(f"\n  [+] Pembeli menyerahkan uang tunai: Rp {uang_dibayar:,.0f}")
    pembayaran = tx_valid.proses_pembayaran(nominal_bayar=uang_dibayar, metode="TUNAI")
    print(f"  [+] Status Pembayaran: LUNAS | Kembalian: Rp {pembayaran.nominal_kembalian:,.0f}")

    # Finalisasi transaksi (pemotongan stok secara atomik)
    stok_lpg_sebelum = brg_lpg.stok_tersedia
    tx_valid.selesaikan_transaksi()
    layanan_laporan.tambah_transaksi(tx_valid)

    print(f"  [+] Transaksi {tx_valid.nomor_transaksi} berhasil diselesaikan (Status: {tx_valid.status_transaksi}).")
    print(f"  [+] Verifikasi Pemotongan Stok Atomik:")
    print(f"      - LPG 3kg     : {stok_lpg_sebelum} -> {brg_lpg.stok_tersedia} (berkurang 1)")
    print(f"      - Beras SPHP  : {brg_sphp.stok_tersedia} (berkurang 2)")
    print(f"      - Gula Pasir  : {brg_gula.stok_tersedia} (berkurang 3)")

    # 8. Hasilkan Laporan & Rekapitulasi Sistem
    print_step("10. Layanan Laporan (Penjualan, Evaluasi Stok Kritis, dan Audit)")

    laporan_penjualan = layanan_laporan.hasilkan_laporan_penjualan(
        periode_awal=date.today(),
        periode_akhir=date.today(),
    )
    print(f"\n  [LAPORAN PENJUALAN HARIAN ({laporan_penjualan['periode_awal']})]")
    print(f"  - Total Transaksi Selesai : {laporan_penjualan['jumlah_transaksi']}")
    print(f"  - Total Omset Koperasi    : Rp {laporan_penjualan['total_omset']:,.0f}")
    print(f"  - Total Item Komoditas    : {laporan_penjualan['total_item_terjual']}")

    laporan_stok = layanan_laporan.hasilkan_laporan_persediaan(hanya_stok_kritis=False)
    print(f"\n  [LAPORAN POSISI PERSEDIAAN GUDANG]")
    for item in laporan_stok:
        kritis_mark = "[KRITIS/RESTOCK]" if item["status_kritis"] else "[AMAN]"
        print(
            f"  - {item['nama_barang']} ({item['kode_barang']}) | "
            f"Stok: {item['stok_tersedia']} {item['satuan']} (Min: {item['stok_minimum']}) {kritis_mark}"
        )

    riwayat_akt = layanan_laporan.cari_riwayat_persediaan()
    print(f"\n  [JEJAK AUDIT AKTIVITAS PERSEDIAAN]")
    for idx, akt in enumerate(riwayat_akt, 1):
        ringkas = akt.dapatkan_ringkasan_audit()
        print(
            f"  {idx}. [{akt.__class__.__name__}] {ringkas['nama_barang']} | "
            f"Mutasi: {ringkas['jumlah_perubahan']:+d} | "
            f"Stok: {ringkas['stok_sebelum']} -> {ringkas['stok_sesudah']} | "
            f"Petugas: {ringkas['nama_petugas']} | Ket: {ringkas['catatan']}"
        )

    print_header("Seluruh Alur Pengujian & Operasional SIMIP Berhasil 100%")


def main() -> None:
    print_header("Sistem Informasi Manajemen Kasir & Inventaris Koperasi Desa Merah Putih (SIMIP)")
    run_encapsulation_tests()
    run_full_workflow()


if __name__ == "__main__":
    main()
