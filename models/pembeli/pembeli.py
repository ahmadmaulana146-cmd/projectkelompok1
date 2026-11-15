from __future__ import annotations
from typing import List, Optional

from models.pembeli.kualifikasi_pembeli import KualifikasiPembeli


class Pembeli:
    """Kelas domain untuk merepresentasikan pembeli / pelanggan koperasi."""

    def __init__(
        self,
        id_pembeli: str,
        nama_pembeli: str,
        alamat_domisili: str,
        nik_terenkripsi: Optional[str] = None,
        tipe_pembeli_umum: bool = True,
        daftar_kualifikasi: Optional[List[KualifikasiPembeli]] = None,
    ) -> None:
        self.id_pembeli = id_pembeli
        self.nama_pembeli = nama_pembeli
        self.alamat_domisili = alamat_domisili
        self.nik_terenkripsi = nik_terenkripsi
        self.tipe_pembeli_umum = tipe_pembeli_umum
        self.daftar_kualifikasi = daftar_kualifikasi or []

    @property
    def id_pembeli(self) -> str:
        return self.__id_pembeli

    @id_pembeli.setter
    def id_pembeli(self, value: str) -> None:
        if not value:
            raise ValueError("ID Pembeli tidak boleh kosong.")
        self.__id_pembeli = value

    @property
    def nama_pembeli(self) -> str:
        return self.__nama_pembeli

    @nama_pembeli.setter
    def nama_pembeli(self, value: str) -> None:
        if not value:
            raise ValueError("Nama pembeli tidak boleh kosong.")
        self.__nama_pembeli = value

    @property
    def nik_terenkripsi(self) -> Optional[str]:
        return self.__nik_terenkripsi

    @nik_terenkripsi.setter
    def nik_terenkripsi(self, value: Optional[str]) -> None:
        if value and len(value) < 8:
            raise ValueError("Format NIK tidak valid (minimal 8 digit).")
        self.__nik_terenkripsi = value or None

    @property
    def nik_tampil_masked(self) -> Optional[str]:
        """NIK tersamar sesuai NFR-07, contoh: 3302********1234."""
        nik = self.__nik_terenkripsi
        if nik is None:
            return None
        return nik[:4] + "*" * (len(nik) - 8) + nik[-4:]

    @property
    def tipe_pembeli_umum(self) -> bool:
        return self.__tipe_pembeli_umum

    @tipe_pembeli_umum.setter
    def tipe_pembeli_umum(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("tipe_pembeli_umum harus bertipe boolean.")
        self.__tipe_pembeli_umum = value

    @property
    def daftar_kualifikasi(self) -> List[KualifikasiPembeli]:
        return list(self.__daftar_kualifikasi)

    @daftar_kualifikasi.setter
    def daftar_kualifikasi(self, value: List[KualifikasiPembeli]) -> None:
        if not isinstance(value, list):
            raise ValueError("daftar_kualifikasi harus berupa list.")
        for item in value:
            if not isinstance(item, KualifikasiPembeli):
                raise ValueError("Setiap elemen daftar kualifikasi harus objek KualifikasiPembeli.")
        self.__daftar_kualifikasi = list(value)

    def tambah_kualifikasi_komoditas(self, kualifikasi: KualifikasiPembeli) -> None:
        """Menambahkan kualifikasi program komoditas pembeli."""
        if not isinstance(kualifikasi, KualifikasiPembeli):
            raise ValueError("kualifikasi harus merupakan instance dari KualifikasiPembeli.")
        self.__daftar_kualifikasi.append(kualifikasi)

    def dapatkan_kategori_pada_program(self, kode_program: str) -> Optional[str]:
        """Mengambil kategori sasaran pembeli pada program komoditas tertentu."""
        kode = kode_program.upper()
        for k in self.__daftar_kualifikasi:
            if k.kode_program_komoditas == kode and k.apakah_masih_berlaku():
                return k.kategori_sasaran
        return None

    def memiliki_kualifikasi_aktif(self, kode_program: str) -> bool:
        """Memeriksa apakah pembeli punya kualifikasi aktif pada program tertentu."""
        return self.dapatkan_kategori_pada_program(kode_program) is not None

    def memiliki_identitas_valid(self) -> bool:
        """Memeriksa apakah pembeli memiliki NIK terdaftar yang valid."""
        return self.__nik_terenkripsi is not None
