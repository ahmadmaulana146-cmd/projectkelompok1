from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, TYPE_CHECKING
import uuid

from models.inventaris.barang import Barang

if TYPE_CHECKING:
    from models.pengguna.petugas_gudang import PetugasGudang


class AktivitasPersediaan(ABC):
    PREFIX_ID: str = "AKT"

    def __init__(
        self,
        barang: Barang,
        petugas: PetugasGudang,
        jumlah_perubahan: int,
        catatan: str = "",
        stok_sebelum: int = 0,
        stok_sesudah: int = 0,
    ) :

        self._id_aktivitas: str = f"{self.PREFIX_ID}-{uuid.uuid4().hex[:8].upper()}"
        self._waktu_aktivitas: datetime = datetime.now()
        self._barang: Barang
        self._petugas: PetugasGudang
        self._jumlah_perubahan: int = 0
        self._stok_sebelum: int = 0
        self._stok_sesudah: int = 0
        self._catatan: str = ""

        self.barang = barang
        self.petugas = petugas
        self.jumlah_perubahan = jumlah_perubahan
        self.stok_sebelum = stok_sebelum
        self.stok_sesudah = stok_sesudah
        self.catatan = catatan


    @property
    def id_aktivitas(self) -> str:
        return self._id_aktivitas

    @property
    def waktu_aktivitas(self) -> datetime:
        return self._waktu_aktivitas

    @property
    def barang(self) -> Barang:
        return self._barang

    @barang.setter
    def barang(self, value: Barang) -> None:
        if value is None:
            raise ValueError("Barang tidak boleh kosong.")
        self._barang = value

    @property
    def petugas(self) -> PetugasGudang:
        return self._petugas

    @petugas.setter
    def petugas(self, value: PetugasGudang) -> None:
        if value is None:
            raise ValueError("Petugas gudang pencatat tidak boleh kosong.")
        self._petugas = value

    @property
    def jumlah_perubahan(self) -> int:
        return self._jumlah_perubahan

    @jumlah_perubahan.setter
    def jumlah_perubahan(self, value: int) -> None:
        self._jumlah_perubahan = value

    @property
    def stok_sebelum(self) -> int:
        return self._stok_sebelum

    @stok_sebelum.setter
    def stok_sebelum(self, value: int) -> None:
        if value < 0:
            raise ValueError("Stok sebelum perubahan tidak boleh negatif.")
        self._stok_sebelum = value

    @property
    def stok_sesudah(self) -> int:
        return self._stok_sesudah

    @stok_sesudah.setter
    def stok_sesudah(self, value: int) -> None:
        if value < 0:
            raise ValueError("Stok sesudah perubahan tidak boleh negatif.")
        self._stok_sesudah = value

    @property
    def catatan(self) -> str:
        return self._catatan

    @catatan.setter
    def catatan(self, value: str) -> None:
        self._catatan = value.strip() if value else ""

    def proses_aktivitas(self) -> bool:
        """Template Method: memvalidasi aktivitas lalu menerapkan perubahan stok."""
        if not self.validasi_aktivitas():
            return False

        self.stok_sebelum = self.barang.stok_tersedia
        self.terapkan_perubahan_stok()
        self.stok_sesudah = self.barang.stok_tersedia
        return True

    @abstractmethod
    def validasi_aktivitas(self) -> bool:
        """Memvalidasi aturan bisnis spesifik sebelum stok diubah."""
        pass

    @abstractmethod
    def terapkan_perubahan_stok(self) -> None:
        """Menerapkan perubahan kuantitas stok pada objek Barang."""
        pass


    def dapatkan_ringkasan_audit(self) -> Dict[str, Any]:
        """Mengembalikan ringkasan jejak audit perubahan stok."""
        return {
            "id_aktivitas": self.id_aktivitas,
            "waktu_aktivitas": self.waktu_aktivitas.isoformat(),
            "id_petugas": self.petugas.id_user,
            "nama_petugas": self.petugas.nama_lengkap,
            "kode_barang": self.barang.kode_barang,
            "nama_barang": self.barang.nama_barang,
            "jumlah_perubahan": self.jumlah_perubahan,
            "stok_sebelum": self.stok_sebelum,
            "stok_sesudah": self.stok_sesudah,
            "catatan": self.catatan,
        }