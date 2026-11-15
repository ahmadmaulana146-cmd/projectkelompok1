from __future__ import annotations
from typing import Dict


class Kategori:

    def __init__(self, id_kategori, nama_kategori, deskripsi):
        self.__id_kategori = ""
        self.__nama_kategori = ""
        self.__deskripsi = ""

        self.id_kategori = id_kategori
        self.nama_kategori = nama_kategori
        self.deskripsi = deskripsi

    @property
    def id_kategori(self):
        return self.__id_kategori

    @id_kategori.setter
    def id_kategori(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Kategori harus berupa string non-kosong.")
        self.__id_kategori = value.strip()

    @property
    def nama_kategori(self):
        return self.__nama_kategori

    @nama_kategori.setter
    def nama_kategori(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama kategori harus berupa string non-kosong.")
        self.__nama_kategori = value.strip()

    @property
    def deskripsi(self):
        return self.__deskripsi

    @deskripsi.setter
    def deskripsi(self, value):
        if not isinstance(value, str):
            raise ValueError("Deskripsi harus berupa string.")
        self.__deskripsi = value.strip()

    def perbarui_info(self, nama_baru, deskripsi_baru):
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
