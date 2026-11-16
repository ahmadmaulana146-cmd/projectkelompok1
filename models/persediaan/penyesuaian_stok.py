from __future__ import annotations
from typing import TYPE_CHECKING

from models.inventaris.barang import Barang
from models.persediaan.aktivitas_persediaan import AktivitasPersediaan

if TYPE_CHECKING:
    from models.pengguna.petugas_gudang import PetugasGudang


class PenyesuaianStok(AktivitasPersediaan):
    """Subclass AktivitasPersediaan untuk pencatatan hasil stock opname (FR-08, BR-10)."""

    PREFIX_ID: str = "ADJ"

    def __init__(
        self,
        barang: Barang,
        petugas: PetugasGudang,
        stok_fisik_hasil_opname: int,
        alasan_penyesuaian: str,
        catatan: str = "",
    ) -> None:
        # 1. Deklarasi atribut private (-) sesuai Tabel Pemetaan & Gambar 5.2
        self.__stok_fisik_hasil_opname: int = 0
        self.__selisih_stok: int = 0
        self.__alasan_penyesuaian: str = ""

        # 2. Mengirim data umum ke superclass
        super().__init__(
            barang=barang,
            petugas=petugas,
            jumlah_perubahan=0,
            catatan=catatan if catatan else f"Opname: {alasan_penyesuaian}",
        )

        # 3. Mengisi dan memvalidasi atribut spesifik PenyesuaianStok
        self.stok_fisik_hasil_opname = stok_fisik_hasil_opname
        self.alasan_penyesuaian = alasan_penyesuaian
        self.__selisih_stok = self.stok_fisik_hasil_opname - self.barang.stok_tersedia
        self.jumlah_perubahan = self.__selisih_stok

    # --- GETTER & SETTER ---

    @property
    def stok_fisik_hasil_opname(self) -> int:
        return self.__stok_fisik_hasil_opname

    @stok_fisik_hasil_opname.setter
    def stok_fisik_hasil_opname(self, value: int) -> None:
        if value < 0:
            raise ValueError("Stok fisik hasil opname tidak boleh bernilai negatif.")
        self.__stok_fisik_hasil_opname = value

    @property
    def selisih_stok(self) -> int:
        return self.__selisih_stok

    @property
    def alasan_penyesuaian(self) -> str:
        return self.__alasan_penyesuaian

    @alasan_penyesuaian.setter
    def alasan_penyesuaian(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Alasan penyesuaian stok wajib diisi (BR-10).")
        self.__alasan_penyesuaian = value.strip()

    # --- IMPLEMENTASI ABSTRACT METHOD (Sesuai Gambar 5.2) ---

    def validasi_aktivitas(self) -> bool:
        """Valid bila stok fisik >= 0 dan alasan penyesuaian terisi (BR-10)."""
        if self.stok_fisik_hasil_opname < 0:
            return False
        if not self.alasan_penyesuaian:
            return False
        return True

    def terapkan_perubahan_stok(self) -> None:
        """Menyelaraskan stok aktual Barang dengan hasil opname fisik."""
        self.__selisih_stok = self.stok_fisik_hasil_opname - self.barang.stok_tersedia
        self.jumlah_perubahan = self.__selisih_stok
        self.barang.sesuaikan_stok_aktual(
            stok_fisik_baru=self.stok_fisik_hasil_opname,
            alasan=f"{self.alasan_penyesuaian} ({self.id_aktivitas})",
        )