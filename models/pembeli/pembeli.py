from __future__ import annotations

from models.pembeli.kualifikasi_pembeli import KualifikasiPembeli


class Pembeli:

    def __init__(
        self,
        id_pembeli,
        nama_pembeli,
        alamat_domisili,
        nik_terenkripsi=None,
        tipe_pembeli_umum=True,
        daftar_kualifikasi=None,
    ):
        self.id_pembeli = id_pembeli
        self.nama_pembeli = nama_pembeli
        self.alamat_domisili = alamat_domisili
        self.nik_terenkripsi = nik_terenkripsi
        self.tipe_pembeli_umum = tipe_pembeli_umum
        self.daftar_kualifikasi = [] if daftar_kualifikasi is None else daftar_kualifikasi

    @property
    def id_pembeli(self):
        return self.__id_pembeli

    @id_pembeli.setter
    def id_pembeli(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Pembeli harus berupa string non-kosong.")
        self.__id_pembeli = value.strip()

    @property
    def nama_pembeli(self):
        return self.__nama_pembeli

    @nama_pembeli.setter
    def nama_pembeli(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama pembeli harus berupa string non-kosong.")
        self.__nama_pembeli = value.strip()

    @property
    def nik_terenkripsi(self):
        return self.__nik_terenkripsi

    @nik_terenkripsi.setter
    def nik_terenkripsi(self, value):
        if value is not None:
            if not isinstance(value, str):
                raise ValueError("NIK harus berupa string atau None.")
            clean_nik = value.strip()
            if 0 < len(clean_nik) < 8:
                raise ValueError("Format NIK tidak valid (minimal 8 karakter).")
            self.__nik_terenkripsi = clean_nik or None
            # Bentuk masked NIK sesuai NFR-07 (contoh: 3302********1234)
            if len(clean_nik) > 8:
                self.__nik_tampil_masked = (
                    clean_nik[:4] + "*" * (len(clean_nik) - 8) + clean_nik[-4:]
                )
            else:
                self.__nik_tampil_masked = "*" * len(clean_nik) if clean_nik else None
        else:
            self.__nik_terenkripsi = None
            self.__nik_tampil_masked = None

    @property
    def nik_tampil_masked(self):
        return self.__nik_tampil_masked

    @nik_tampil_masked.setter
    def nik_tampil_masked(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("nik_tampil_masked harus berupa string atau None.")
        self.__nik_tampil_masked = value

    @property
    def alamat_domisili(self):
        return self.__alamat_domisili

    @alamat_domisili.setter
    def alamat_domisili(self, value):
        if not isinstance(value, str):
            raise ValueError("Alamat domisili harus berupa string.")
        self.__alamat_domisili = value.strip()

    @property
    def tipe_pembeli_umum(self):
        return self.__tipe_pembeli_umum

    @tipe_pembeli_umum.setter
    def tipe_pembeli_umum(self, value):
        if not isinstance(value, bool):
            raise ValueError("tipe_pembeli_umum harus bertipe boolean.")
        self.__tipe_pembeli_umum = value

    @property
    def daftar_kualifikasi(self):
        return list(self.__daftar_kualifikasi)

    @daftar_kualifikasi.setter
    def daftar_kualifikasi(self, value):
        if not isinstance(value, list):
            raise ValueError("daftar_kualifikasi harus berupa list.")
        for item in value:
            if not isinstance(item, KualifikasiPembeli):
                raise ValueError("Setiap elemen daftar kualifikasi harus objek KualifikasiPembeli.")
        self.__daftar_kualifikasi = list(value)

    def tambah_kualifikasi_komoditas(self, kualifikasi):
        """Menambahkan sertifikasi/kualifikasi program komoditas pembeli."""
        if not isinstance(kualifikasi, KualifikasiPembeli):
            raise ValueError("kualifikasi harus merupakan instance dari KualifikasiPembeli.")
        self.__daftar_kualifikasi.append(kualifikasi)

    def memiliki_kualifikasi_aktif(self, kode_program):
        """Memeriksa apakah pembeli memiliki kualifikasi aktif pada kode program tertentu."""
        return self.dapatkan_kategori_pada_program(kode_program) is not None

    def dapatkan_kategori_pada_program(self, kode_program):
        """Mengambil kategori sasaran pembeli pada suatu program komoditas tertentu."""
        if not isinstance(kode_program, str) or not kode_program.strip():
            raise ValueError("Kode program harus berupa string non-kosong.")
        kode_clean = kode_program.strip().upper()
        for k in self.__daftar_kualifikasi:
            if k.kode_program_komoditas == kode_clean and k.apakah_masih_berlaku():
                return k.kategori_sasaran
        return None

    def memiliki_identitas_valid(self):
        """Memeriksa apakah pembeli memiliki NIK terdaftar yang valid."""
        return self.__nik_terenkripsi is not None
