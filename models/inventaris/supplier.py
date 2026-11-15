from __future__ import annotations
from typing import Dict


class Supplier:
    def __init__(
        self,
        id_supplier,
        nama_supplier,
        jenis_instansi,
        kontak_telepon,
        alamat,
    ):
        self.__id_supplier = ""
        self.__nama_supplier = ""
        self.__jenis_instansi = ""
        self.__kontak_telepon = ""
        self.__alamat = ""

        self.id_supplier = id_supplier
        self.nama_supplier = nama_supplier
        self.jenis_instansi = jenis_instansi
        self.kontak_telepon = kontak_telepon
        self.alamat = alamat

    @property
    def id_supplier(self):
        return self.__id_supplier

    @id_supplier.setter
    def id_supplier(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Supplier harus berupa string non-kosong.")
        self.__id_supplier = value.strip()

    @property
    def nama_supplier(self):
        return self.__nama_supplier

    @nama_supplier.setter
    def nama_supplier(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama supplier harus berupa string non-kosong.")
        self.__nama_supplier = value.strip()

    @property
    def jenis_instansi(self):
        return self.__jenis_instansi

    @jenis_instansi.setter
    def jenis_instansi(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Jenis instansi harus berupa string non-kosong.")
        self.__jenis_instansi = value.strip()

    @property
    def kontak_telepon(self):
        return self.__kontak_telepon

    @kontak_telepon.setter
    def kontak_telepon(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Kontak telepon harus berupa string non-kosong.")
        self.__kontak_telepon = value.strip()

    @property
    def alamat(self):
        return self.__alamat

    @alamat.setter
    def alamat(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Alamat harus berupa string non-kosong.")
        self.__alamat = value.strip()

    def perbarui_kontak(self, telepon, alamat):
        """Memperbarui nomor kontak dan alamat supplier."""
        self.kontak_telepon = telepon
        self.alamat = alamat

    def info_supplier(self) -> Dict[str, str]:
        """Mengembalikan data profil pemasok."""
        return {
            "id_supplier": self.id_supplier,
            "nama_supplier": self.nama_supplier,
            "jenis_instansi": self.jenis_instansi,
            "kontak_telepon": self.kontak_telepon,
            "alamat": self.alamat,
        }
