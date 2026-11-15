from __future__ import annotations
from typing import Dict


class Supplier:
    """Kelas domain untuk merepresentasikan pemasok komoditas."""

    def __init__(
        self,
        id_supplier: str,
        nama_supplier: str,
        jenis_instansi: str,
        kontak_telepon: str,
        alamat: str,
    ) -> None:
        self.__id_supplier: str = ""
        self.__nama_supplier: str = ""
        self.__jenis_instansi: str = ""
        self.__kontak_telepon: str = ""
        self.__alamat: str = ""

        self.id_supplier = id_supplier
        self.nama_supplier = nama_supplier
        self.jenis_instansi = jenis_instansi
        self.kontak_telepon = kontak_telepon
        self.alamat = alamat

    @property
    def id_supplier(self) -> str:
        return self.__id_supplier

    @id_supplier.setter
    def id_supplier(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Supplier harus berupa string non-kosong.")
        self.__id_supplier = value.strip()

    @property
    def nama_supplier(self) -> str:
        return self.__nama_supplier

    @nama_supplier.setter
    def nama_supplier(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama supplier harus berupa string non-kosong.")
        self.__nama_supplier = value.strip()

    @property
    def jenis_instansi(self) -> str:
        return self.__jenis_instansi

    @jenis_instansi.setter
    def jenis_instansi(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Jenis instansi harus berupa string non-kosong.")
        self.__jenis_instansi = value.strip()

    @property
    def kontak_telepon(self) -> str:
        return self.__kontak_telepon

    @kontak_telepon.setter
    def kontak_telepon(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Kontak telepon harus berupa string non-kosong.")
        self.__kontak_telepon = value.strip()

    @property
    def alamat(self) -> str:
        return self.__alamat

    @alamat.setter
    def alamat(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Alamat harus berupa string non-kosong.")
        self.__alamat = value.strip()

    def perbarui_kontak(self, telepon: str, alamat: str) -> None:
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
