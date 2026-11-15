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
        self.__id_pembeli: str = ""
        self.__nama_pembeli: str = ""
        self.__nik_terenkripsi: Optional[str] = None
        self.__nik_tampil_masked: Optional[str] = None
        self.__alamat_domisili: str = ""
        self.__tipe_pembeli_umum: bool = True
        self.__daftar_kualifikasi: List[KualifikasiPembeli] = []

        self.id_pembeli = id_pembeli
        self.nama_pembeli = nama_pembeli
        self.alamat_domisili = alamat_domisili
        self.nik_terenkripsi = nik_terenkripsi
        self.tipe_pembeli_umum = tipe_pembeli_umum
        self.daftar_kualifikasi = (
            daftar_kualifikasi if daftar_kualifikasi is not None else []
        )

    @property
    def id_pembeli(self) -> str:
        return self.__id_pembeli

    @id_pembeli.setter
    def id_pembeli(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Pembeli harus berupa string non-kosong.")
        self.__id_pembeli = value.strip()

    @property
    def nama_pembeli(self) -> str:
        return self.__nama_pembeli

    @nama_pembeli.setter
    def nama_pembeli(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama pembeli harus berupa string non-kosong.")
        self.__nama_pembeli = value.strip()

    @property
    def nik_terenkripsi(self) -> Optional[str]:
        return self.__nik_terenkripsi

    @nik_terenkripsi.setter
    def nik_terenkripsi(self, value: Optional[str]) -> None:
        if value is not None:
            if not isinstance(value, str):
                raise ValueError("NIK harus berupa string atau None.")
            clean_nik = value.strip()
            if len(clean_nik) > 0 and len(clean_nik) < 8:
                raise ValueError("Format NIK tidak valid (minimal 8 digit).")
            self.__nik_terenkripsi = clean_nik
            if len(clean_nik) >= 8:
                self.__nik_tampil_masked = (
                    clean_nik[:4] + "*" * (len(clean_nik) - 8) + clean_nik[-4:]
                )
            else:
                self.__nik_tampil_masked = "*" * len(clean_nik)
        else:
            self.__nik_terenkripsi = None
            self.__nik_tampil_masked = None

    @property
    def nik_tampil_masked(self) -> Optional[str]:
        return self.__nik_tampil_masked

    @nik_tampil_masked.setter
    def nik_tampil_masked(self, value: Optional[str]) -> None:
        if value is not None and not isinstance(value, str):
            raise ValueError("nik_tampil_masked harus berupa string atau None.")
        self.__nik_tampil_masked = value

    @property
    def alamat_domisili(self) -> str:
        return self.__alamat_domisili

    @alamat_domisili.setter
    def alamat_domisili(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("Alamat domisili harus berupa string.")
        self.__alamat_domisili = value.strip()

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
                raise ValueError("Setiap elemen daftar kualifikasi harus merupakan objek KualifikasiPembeli.")
        self.__daftar_kualifikasi = list(value)

    def tambah_kualifikasi_komoditas(self, kualifikasi: KualifikasiPembeli) -> None:
        """Menambahkan sertifikasi/kualifikasi program komoditas pembeli."""
        if not isinstance(kualifikasi, KualifikasiPembeli):
            raise ValueError("kualifikasi harus merupakan instance dari KualifikasiPembeli.")
        self.__daftar_kualifikasi.append(kualifikasi)

    def memiliki_kualifikasi_aktif(self, kode_program: str) -> bool:
        """Memeriksa apakah pembeli memiliki kualifikasi aktif pada kode program tertentu."""
        kode_clean = kode_program.strip().upper()
        for k in self.__daftar_kualifikasi:
            if k.kode_program_komoditas == kode_clean and k.apakah_masih_berlaku():
                return True
        return False

    def dapatkan_kategori_pada_program(self, kode_program: str) -> Optional[str]:
        """Mengambil kategori sasaran pembeli pada suatu program komoditas tertentu."""
        kode_clean = kode_program.strip().upper()
        for k in self.__daftar_kualifikasi:
            if k.kode_program_komoditas == kode_clean and k.apakah_masih_berlaku():
                return k.kategori_sasaran
        return None

    def memiliki_identitas_valid(self) -> bool:
        """Memeriksa apakah pembeli memiliki NIK terdaftar yang valid."""
        if not self.__nik_terenkripsi:
            return False
        return len(self.__nik_terenkripsi) >= 8
