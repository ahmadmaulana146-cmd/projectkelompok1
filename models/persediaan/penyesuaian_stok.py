from __future__ import annotations
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from models.inventaris.barang import Barang
from models.persediaan.aktivitas_persediaan import AktivitasPersediaan
from models.pembeli.hasil_validasi import HasilValidasi

if TYPE_CHECKING:
    from models.pengguna.petugas_gudang import PetugasGudang


class PenyesuaianStok(AktivitasPersediaan):
    """Subclass AktivitasPersediaan untuk sinkronisasi stok hasil pemeriksaan fisik (stock opname)."""

    def __init__(
        self,
        id_aktivitas: str,
        barang: Barang,
        petugas: PetugasGudang,
        stok_fisik_hasil_opname: int,
        alasan_penyesuaian: str,
        catatan: str = "",
        waktu_aktivitas: Optional[datetime] = None,
    ) -> None:
        selisih_awal = stok_fisik_hasil_opname - barang.stok_tersedia
        super().__init__(
            id_aktivitas=id_aktivitas,
            barang=barang,
            petugas=petugas,
            jumlah_perubahan=selisih_awal,
            catatan=catatan if catatan else f"Opname: {alasan_penyesuaian}",
            waktu_aktivitas=waktu_aktivitas,
        )
        self.__stok_fisik_hasil_opname: int = 0
        self.__selisih_stok: int = 0
        self.__alasan_penyesuaian: str = ""

        self.stok_fisik_hasil_opname = stok_fisik_hasil_opname
        self.alasan_penyesuaian = alasan_penyesuaian
        self.hitung_selisih()

    @property
    def stok_fisik_hasil_opname(self) -> int:
        return self.__stok_fisik_hasil_opname

    @stok_fisik_hasil_opname.setter
    def stok_fisik_hasil_opname(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Stok fisik hasil opname harus berupa integer non-negatif (diberikan: {value}).")
        self.__stok_fisik_hasil_opname = value

    @property
    def selisih_stok(self) -> int:
        return self.__selisih_stok

    @selisih_stok.setter
    def selisih_stok(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Selisih stok harus berupa integer.")
        self.__selisih_stok = value

    @property
    def alasan_penyesuaian(self) -> str:
        return self.__alasan_penyesuaian

    @alasan_penyesuaian.setter
    def alasan_penyesuaian(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Alasan penyesuaian stok wajib diisi (BR-10).")
        self.__alasan_penyesuaian = value.strip()

    def hitung_selisih(self) -> int:
        """Menghitung selisih antara stok fisik hasil opname dengan stok tercatat pada sistem."""
        self.selisih_stok = self.stok_fisik_hasil_opname - self._barang.stok_tersedia
        self.jumlah_perubahan = self.selisih_stok
        return self.selisih_stok

    def validasi_aktivitas(self) -> HasilValidasi:
        """Memvalidasi pemenuhan syarat penyesuaian stok opname (BR-10)."""
        if not self.__alasan_penyesuaian:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_ALASAN_EMPTY",
                pesan_validasi="Penyesuaian stok harus disertai alasan perubahan (BR-10).",
            )
        if self.__stok_fisik_hasil_opname < 0:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_STOK_FISIK_INVALID",
                pesan_validasi="Stok fisik hasil opname tidak boleh negatif.",
            )
        self.hitung_selisih()
        if self.__selisih_stok == 0:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_SELISIH_NOL",
                pesan_validasi="Stok fisik sama dengan stok sistem, tidak ada perubahan yang perlu disesuaikan.",
            )
        return HasilValidasi(
            status_valid=True,
            kode_status="OK_PENYESUAIAN_STOK",
            pesan_validasi=f"Penyesuaian stok valid dengan selisih {self.__selisih_stok}.",
        )

    def terapkan_perubahan_stok(self) -> None:
        """Menerapkan penyesuaian stok aktual pada objek Barang (FR-08, BR-10)."""
        self._barang.sesuaikan_stok_aktual(
            stok_fisik_baru=self.__stok_fisik_hasil_opname,
            alasan=self.__alasan_penyesuaian,
        )
