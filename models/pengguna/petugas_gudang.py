from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING

from models.pengguna.user import User
from models.persediaan.barang_masuk import BarangMasuk
from models.persediaan.barang_keluar import BarangKeluar
from models.persediaan.penyesuaian_stok import PenyesuaianStok

if TYPE_CHECKING:
    from models.inventaris.barang import Barang
    from models.inventaris.supplier import Supplier


class PetugasGudang(User):
    def __init__(
        self,
        id_user,
        username,
        password_hash,
        nama_lengkap,
        status_aktif = True,
    ) -> None:
        super().__init__(
            id_user=id_user,
            username=username,
            password_hash=password_hash,
            nama_lengkap=nama_lengkap,
            peran="PetugasGudang",
            status_aktif=status_aktif,
        )

    def dapatkan_hak_akses(self) -> List[str]:
        return [
            "catat_barang_masuk",
            "catat_barang_keluar",
            "catat_penyesuaian_stok",
            "pantau_stok",
            "lihat_riwayat_stok",
        ]

    def catat_barang_masuk(
        self,
        barang: Barang,
        supplier: Supplier,
        jumlah: int,
        no_ref: str,
        harga_beli: Decimal,
        ket: str = "",
    ) -> BarangMasuk:
        # id_aktivitas dan waktu_aktivitas sudah otomatis dibuat oleh sistem
        aktivitas = BarangMasuk(
            barang=barang,
            petugas=self,
            supplier=supplier,
            jumlah_perubahan=jumlah,
            nomor_referensi_surat_jalan=no_ref,
            harga_beli_satuan=harga_beli,
            catatan=ket,
        )
        aktivitas.proses_aktivitas()
        return aktivitas

    def catat_barang_keluar(
        self,
        barang: Barang,
        jumlah: int,
        tujuan: str,
        penerima: str,
        ket: str = "",
    ) -> BarangKeluar:
        # id_aktivitas dan waktu_aktivitas sudah otomatis dibuat oleh sistem
        aktivitas = BarangKeluar(
            barang=barang,
            petugas=self,
            jumlah_perubahan=jumlah,
            jenis_keperluan_keluar=tujuan,
            penerima_internal=penerima,
            catatan=ket,
        )
        aktivitas.proses_aktivitas()
        return aktivitas

    def catat_penyesuaian_stok(
        self,
        barang: Barang,
        stok_fisik: int,
        alasan: str,
        ket: str = "",
    ) -> PenyesuaianStok:
        # id_aktivitas dan waktu_aktivitas sudah otomatis dibuat oleh sistem
        aktivitas = PenyesuaianStok(
            barang=barang,
            petugas=self,
            stok_fisik_hasil_opname=stok_fisik,
            alasan_penyesuaian=alasan,
            catatan=ket,
        )
        aktivitas.proses_aktivitas()
        return aktivitas
