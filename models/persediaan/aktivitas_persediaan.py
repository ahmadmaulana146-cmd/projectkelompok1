from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from models.inventaris.barang import Barang
from models.pembeli.hasil_validasi import HasilValidasi

if TYPE_CHECKING:
    from models.pengguna.petugas_gudang import PetugasGudang


class AktivitasPersediaan(ABC):
    """Abstract Base Class untuk seluruh aktivitas perubahan stok inventaris gudang (Template Method)."""

    def __init__(
             self,
             petugas: PetugasGudang,
             id_aktivitas: str,
             waktu_aktivitas: datetime,
             barang: Barang,
             jumlah_perubahan: int,
             catatan: str,
             stok_sebelum: int = 0,
             stok_sesudah: int = 0,
            ):

        self._id_aktivitas: str = id_aktivitas
        self._waktu_aktivitas: datetime = waktu_aktivitas
        self._barang: Barang = barang
        self._petugas: PetugasGudang = petugas
        self._jumlah_perubahan: int = jumlah_perubahan
        self._stok_sebelum: int = stok_sebelum
        self._stok_sesudah: int = stok_sesudah
        self._catatan: str = catatan

    @property
    def id_aktivitas(self) :
        return self._id_aktivitas

    @id_aktivitas.setter
    def id_aktivitas(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Aktivitas harus berupa string non-kosong.")
        self._id_aktivitas = value.strip()

    @property
    def waktu_aktivitas(self) :
        return self._waktu_aktivitas

    @waktu_aktivitas.setter
    def waktu_aktivitas(self, value: datetime) :
        if not isinstance(value, datetime):
            raise ValueError("Waktu aktivitas harus bertipe datetime.")
        self._waktu_aktivitas = value

    @property
    def barang(self) :
        if self._barang is None:
            raise ValueError("Barang belum diinisialisasi.")
        return self._barang

    @barang.setter
    def barang(self, value: Barang) :
        if not isinstance(value, Barang):
            raise ValueError("barang harus merupakan instance dari kelas Barang.")
        self._barang = value

    @property
    def petugas(self) :
        if self._petugas is None:
            raise ValueError("Petugas belum diinisialisasi.")
        return self._petugas

    @petugas.setter
    def petugas(self, value: PetugasGudang) :
        from models.pengguna.petugas_gudang import PetugasGudang
        if not isinstance(value, PetugasGudang):
            raise ValueError("petugas harus merupakan instance dari kelas PetugasGudang.")
        self._petugas = value

    @property
    def jumlah_perubahan(self) :
        return self._jumlah_perubahan

    @jumlah_perubahan.setter
    def jumlah_perubahan(self, value: int) :
        if not isinstance(value, int):
            raise ValueError("Jumlah perubahan stok harus berupa integer.")
        self._jumlah_perubahan = value

    @property
    def stok_sebelum(self) :
        return self._stok_sebelum

    @stok_sebelum.setter
    def stok_sebelum(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("Stok sebelum harus berupa integer non-negatif.")
        self._stok_sebelum = value

    @property
    def stok_sesudah(self) :
        return self._stok_sesudah

    @stok_sesudah.setter
    def stok_sesudah(self, value: int) :
        if not isinstance(value, int) or value < 0:
            raise ValueError("Stok sesudah harus berupa integer non-negatif.")
        self._stok_sesudah = value

    @property
    def catatan(self) :
        return self._catatan

    @catatan.setter
    def catatan(self, value: str) :
        if not isinstance(value, str):
            raise ValueError("Catatan aktivitas harus bertipe string.")
        self._catatan = value.strip()

    def proses_aktivitas(self) :
        hasil_validasi = self.validasi_aktivitas()
        if not hasil_validasi.apakah_lolos():
            return hasil_validasi

        self.stok_sebelum = self.barang.stok_tersedia
        self.terapkan_perubahan_stok()
        self.stok_sesudah = self.barang.stok_tersedia
        return hasil_validasi

    @abstractmethod
    def validasi_aktivitas(self) :
        raise NotImplementedError

    @abstractmethod
    def terapkan_perubahan_stok(self) :
        raise NotImplementedError

    def dapatkan_ringkasan_audit(self) :
        return {
            "id_petugas": self.petugas.id_user,
            "nama_petugas": self.petugas.nama_lengkap,
            "id_aktivitas": self.id_aktivitas,
            "waktu_aktivitas": self.waktu_aktivitas,
            "kode_barang": self.barang.kode_barang,
            "nama_barang": self.barang.nama_barang,
            "jumlah_perubahan": self.jumlah_perubahan,
            "stok_sebelum": self.stok_sebelum,
            "stok_sesudah": self.stok_sesudah,
            "catatan": self.catatan,
        }
