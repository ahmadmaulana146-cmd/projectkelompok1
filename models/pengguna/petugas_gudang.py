from __future__ import annotations
import uuid
from decimal import Decimal
from typing import List, TYPE_CHECKING

from models.pengguna.user import User

if TYPE_CHECKING:
    from models.inventaris.barang import Barang
    from models.inventaris.supplier import Supplier
    from models.persediaan.barang_masuk import BarangMasuk
    from models.persediaan.barang_keluar import BarangKeluar
    from models.persediaan.penyesuaian_stok import PenyesuaianStok


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
        no_ref,
        harga_beli: Decimal,
        ket,
    ) -> BarangMasuk:
        from models.persediaan.barang_masuk import BarangMasuk
        id_akt = f"IN-{uuid.uuid4().hex[:8].upper()}"
        aktivitas = BarangMasuk(
            id_aktivitas=id_akt,
            barang=barang,
            petugas=self,
            jumlah_perubahan=jumlah,
            catatan=ket,
            supplier=supplier,
            nomor_referensi_surat_jalan=no_ref,
            harga_beli_satuan=harga_beli,
        )
        hasil = aktivitas.proses_aktivitas()
        if not hasil.apakah_lolos():
            raise ValueError(f"Gagal mencatat barang masuk: {hasil.pesan_validasi}")
        return aktivitas

    def catat_barang_keluar(
        self,
        barang: Barang,
        jumlah: int,
        tujuan,
        penerima,
        ket,
    ) -> BarangKeluar:
        from models.persediaan.barang_keluar import BarangKeluar
        id_akt = f"OUT-{uuid.uuid4().hex[:8].upper()}"
        aktivitas = BarangKeluar(
            id_aktivitas=id_akt,
            barang=barang,
            petugas=self,
            jumlah_perubahan=jumlah,
            catatan=ket,
            jenis_keperluan_keluar=tujuan,
            penerima_internal=penerima,
        )
        hasil = aktivitas.proses_aktivitas()
        if not hasil.apakah_lolos():
            raise ValueError(f"Gagal mencatat barang keluar: {hasil.pesan_validasi}")
        return aktivitas

    def catat_penyesuaian_stok(
        self,
        barang: Barang,
        stok_fisik: int,
        alasan,
    ) -> PenyesuaianStok:
        from models.persediaan.penyesuaian_stok import PenyesuaianStok
        id_akt = f"ADJ-{uuid.uuid4().hex[:8].upper()}"
        aktivitas = PenyesuaianStok(
            id_aktivitas=id_akt,
            barang=barang,
            petugas=self,
            stok_fisik_hasil_opname=stok_fisik,
            alasan_penyesuaian=alasan,
            catatan=f"Penyesuaian stok fisik opname: {alasan}",
        )
        hasil = aktivitas.proses_aktivitas()
        if not hasil.apakah_lolos():
            raise ValueError(f"Gagal mencatat penyesuaian stok: {hasil.pesan_validasi}")
        return aktivitas
