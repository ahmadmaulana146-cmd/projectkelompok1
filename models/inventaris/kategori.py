from __future__ import annotations
from typing import Dict


class Kategori:
    """Kelas domain untuk merepresentasikan kategori komoditas/barang."""

    def __init__(self, id_kategori: str, nama_kategori: str, deskripsi: str) -> None:
        self.__id_kategori: str = ""
        self.__nama_kategori: str = ""
        self.__deskripsi: str = ""

        self.id_kategori = id_kategori
        self.nama_kategori = nama_kategori
        self.deskripsi = deskripsi

    @property
    def id_kategori(self) -> str:
        return self.__id_kategori

    @id_kategori.setter
    def id_kategori(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Kategori harus berupa string non-kosong.")
        self.__id_kategori = value.strip()

    @property
    def nama_kategori(self) -> str:
        return self.__nama_kategori

    @nama_kategori.setter
    def nama_kategori(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama kategori harus berupa string non-kosong.")
        self.__nama_kategori = value.strip()

    @property
    def deskripsi(self) -> str:
        return self.__deskripsi

    @deskripsi.setter
    def deskripsi(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Deskripsi harus berupa string.")
        self.__deskripsi = value.strip()

    def perbarui_info(self, nama_baru: str, deskripsi_baru: str) -> None:
        """Memperbarui informasi nama dan deskripsi kategori."""
        self.nama_kategori = nama_baru
        self.deskripsi = deskripsi_baru

    def info_kategori(self) -> Dict[str, str]:
        """Mengembalikan informasi kategori dalam format kamus/dictionary."""
        return {
            "id_kategori": self.id_kategori,
            "nama_kategori": self.nama_kategori,
            "deskripsi": self.deskripsi,
        }
