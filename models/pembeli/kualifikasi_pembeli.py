from __future__ import annotations
from datetime import date
from typing import Any, Dict, Optional


class KualifikasiPembeli:

    def __init__(
        self,
        id_kualifikasi,
        kode_program_komoditas,
        kategori_sasaran,
        nomor_dokumen_pendukung = None,
        status_verifikasi = True,
        tanggal_berlaku_sampai = None,
    ):
        self.__id_kualifikasi = ""
        self.__kode_program_komoditas = ""
        self.__kategori_sasaran = ""
        self.__nomor_dokumen_pendukung = None
        self.__status_verifikasi = False
        self.__tanggal_berlaku_sampai = None

        self.id_kualifikasi = id_kualifikasi
        self.kode_program_komoditas = kode_program_komoditas
        self.kategori_sasaran = kategori_sasaran
        self.nomor_dokumen_pendukung = nomor_dokumen_pendukung
        self.status_verifikasi = status_verifikasi
        self.tanggal_berlaku_sampai = tanggal_berlaku_sampai

    @property
    def id_kualifikasi(self):
        return self.__id_kualifikasi

    @id_kualifikasi.setter
    def id_kualifikasi(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Kualifikasi harus berupa string non-kosong.")
        self.__id_kualifikasi = value.strip()

    @property
    def kode_program_komoditas(self):
        return self.__kode_program_komoditas

    @kode_program_komoditas.setter
    def kode_program_komoditas(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Kode program komoditas harus berupa string non-kosong.")
        self.__kode_program_komoditas = value.strip().upper()

    @property
    def kategori_sasaran(self):
        return self.__kategori_sasaran

    @kategori_sasaran.setter
    def kategori_sasaran(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Kategori sasaran harus berupa string non-kosong.")
        self.__kategori_sasaran = value.strip().upper()

    @property
    def nomor_dokumen_pendukung(self):
        return self.__nomor_dokumen_pendukung

    @nomor_dokumen_pendukung.setter
    def nomor_dokumen_pendukung(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("Nomor dokumen pendukung harus berupa string atau None.")
        self.__nomor_dokumen_pendukung = value.strip() if value else None

    @property
    def status_verifikasi(self):
        return self.__status_verifikasi

    @status_verifikasi.setter
    def status_verifikasi(self, value):
        if not isinstance(value, bool):
            raise ValueError("Status verifikasi harus bertipe boolean.")
        self.__status_verifikasi = value

    @property
    def tanggal_berlaku_sampai(self):
        return self.__tanggal_berlaku_sampai

    @tanggal_berlaku_sampai.setter
    def tanggal_berlaku_sampai(self, value):
        if value is not None and not isinstance(value, date):
            raise ValueError("Tanggal berlaku sampai harus berupa objek date atau None.")
        self.__tanggal_berlaku_sampai = value

    def apakah_masih_berlaku(self):
        """Memeriksa apakah kualifikasi telah terverifikasi dan belum kedaluwarsa."""
        if not self.status_verifikasi:
            return False
        if self.tanggal_berlaku_sampai is not None:
            return self.tanggal_berlaku_sampai >= date.today()
        return True

    def info_kualifikasi(self):
        """Mengembalikan representasi kamus dari data kualifikasi."""
        return {
            "id_kualifikasi": self.id_kualifikasi,
            "kode_program_komoditas": self.kode_program_komoditas,
            "kategori_sasaran": self.kategori_sasaran,
            "nomor_dokumen_pendukung": self.nomor_dokumen_pendukung,
            "status_verifikasi": self.status_verifikasi,
            "tanggal_berlaku_sampai": (
                self.tanggal_berlaku_sampai.isoformat()
                if self.tanggal_berlaku_sampai
                else None
            ),
            "masih_berlaku": self.apakah_masih_berlaku(),
        }
