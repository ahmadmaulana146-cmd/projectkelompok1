from __future__ import annotations
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from models.inventaris.barang import Barang
from models.persediaan.aktivitas_persediaan import AktivitasPersediaan
from models.pembeli.hasil_validasi import HasilValidasi

if TYPE_CHECKING:
    from models.pengguna.petugas_gudang import PetugasGudang


class BarangKeluar(AktivitasPersediaan):
    """Subclass AktivitasPersediaan untuk pencatatan pengeluaran barang nonpenjualan (rusak, kedaluwarsa, internal)."""

    def __init__(self, id_aktivitas: str, barang: Barang,
        petugas: PetugasGudang,
        jumlah_perubahan: int,
        catatan: str,
        jenis_keperluan_keluar: str,
        penerima_internal: str,
        waktu_aktivitas: Optional[datetime] = None,
    ) :
        super().__init__(
            id_aktivitas=id_aktivitas,
            barang=barang,
            petugas=petugas,
            jumlah_perubahan=-abs(jumlah_perubahan) if jumlah_perubahan != 0 else 0,
            catatan=catatan,
            waktu_aktivitas=waktu_aktivitas,
        )
        self.__jenis_keperluan_keluar: str = ""
        self.__penerima_internal: str = ""

        self.jenis_keperluan_keluar = jenis_keperluan_keluar
        self.penerima_internal = penerima_internal

    @property
    def jenis_keperluan_keluar(self) -> str:
        return self.__jenis_keperluan_keluar

    @jenis_keperluan_keluar.setter
    def jenis_keperluan_keluar(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Jenis keperluan pengeluaran harus berupa string non-kosong.")
        self.__jenis_keperluan_keluar = value.strip()

    @property
    def penerima_internal(self) -> str:
        return self.__penerima_internal

    @penerima_internal.setter
    def penerima_internal(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama penerima internal harus berupa string non-kosong.")
        self.__penerima_internal = value.strip()

    def validasi_aktivitas(self) -> HasilValidasi:
        """Memvalidasi bahwa jumlah > 0, stok gudang mencukupi, dan identitas keperluan terisi."""
        kuantitas = abs(self._jumlah_perubahan)
        if kuantitas <= 0:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_QTY_INVALID",
                pesan_validasi=f"Jumlah pengeluaran harus lebih dari 0 (diberikan: {kuantitas}).",
            )
        if not self._barang.apakah_stok_mencukupi(kuantitas):
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_STOK_KURANG",
                pesan_validasi=(
                    f"Stok barang '{self._barang.nama_barang}' tidak mencukupi untuk dikeluarkan. "
                    f"Stok tersedia: {self._barang.stok_tersedia}, diminta: {kuantitas}."
                ),
            )
        if not self.__jenis_keperluan_keluar:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_KEPERLUAN_EMPTY",
                pesan_validasi="Jenis keperluan pengeluaran barang wajib diisi.",
            )
        if not self.__penerima_internal:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_PENERIMA_EMPTY",
                pesan_validasi="Penerima internal barang wajib diisi.",
            )
        return HasilValidasi(
            status_valid=True,
            kode_status="OK_BARANG_KELUAR",
            pesan_validasi="Pengeluaran barang nonpenjualan valid.",
        )

    def terapkan_perubahan_stok(self) -> None:
        """Mengurangi stok barang inventaris untuk keperluan nonpenjualan (BR-04)."""
        kuantitas = abs(self._jumlah_perubahan)
        self._barang.kurangi_stok(
            kuantitas,
            sumber=f"Keluar nonpenjualan ({self.__jenis_keperluan_keluar}) - Penerima: {self.__penerima_internal}",
        )
