from __future__ import annotations
from typing import TYPE_CHECKING

from models.inventaris.barang import Barang
from models.persediaan.aktivitas_persediaan import AktivitasPersediaan

if TYPE_CHECKING:
    from models.pengguna.petugas_gudang import PetugasGudang


class BarangKeluar(AktivitasPersediaan):
    """Subclass AktivitasPersediaan untuk pencatatan pengeluaran nonpenjualan (FR-07, BR-04)."""

    PREFIX_ID: str = "OUT"

    def __init__(
        self,
        barang: Barang,
        petugas: PetugasGudang,
        jumlah_perubahan: int,
        jenis_keperluan_keluar: str,
        penerima_internal: str,
        catatan: str = "",
    ) -> None:
        # 1. Deklarasi atribut private (-) sesuai Tabel Pemetaan & Gambar 5.2
        self.__jenis_keperluan_keluar: str = ""
        self.__penerima_internal: str = ""

        # 2. Mengirim data umum ke superclass (bernilai negatif sebagai tanda pengurangan stok)
        super().__init__(
            barang=barang,
            petugas=petugas,
            jumlah_perubahan=-abs(jumlah_perubahan) if jumlah_perubahan != 0 else 0,
            catatan=catatan,
        )

        # 3. Mengisi dan memvalidasi atribut spesifik BarangKeluar
        self.jenis_keperluan_keluar = jenis_keperluan_keluar
        self.penerima_internal = penerima_internal

    # --- GETTER & SETTER ---

    @property
    def jenis_keperluan_keluar(self) -> str:
        return self.__jenis_keperluan_keluar

    @jenis_keperluan_keluar.setter
    def jenis_keperluan_keluar(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Jenis keperluan keluar wajib diisi (misal: rusak, kedaluwarsa, internal).")
        self.__jenis_keperluan_keluar = value.strip()

    @property
    def penerima_internal(self) -> str:
        return self.__penerima_internal

    @penerima_internal.setter
    def penerima_internal(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Penerima internal / penanggung jawab wajib diisi.")
        self.__penerima_internal = value.strip()

    # --- IMPLEMENTASI ABSTRACT METHOD (Sesuai Gambar 5.2) ---

    def validasi_aktivitas(self) -> bool:
        """Valid bila kuantitas > 0, stok mencukupi, serta keperluan & penerima terisi."""
        kuantitas_keluar = abs(self.jumlah_perubahan)
        if kuantitas_keluar <= 0:
            return False
        if not self.jenis_keperluan_keluar or not self.penerima_internal:
            return False
        if not self.barang.apakah_stok_mencukupi(kuantitas_keluar):
            return False
        return True

    def terapkan_perubahan_stok(self) -> None:
        """Mengurangi stok pada objek Barang (BR-04)."""
        self.barang.kurangi_stok(
            jumlah=abs(self.jumlah_perubahan),
            sumber=f"BARANG_KELUAR ({self.id_aktivitas})",
        )