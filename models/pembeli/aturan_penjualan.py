from __future__ import annotations
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING

from models.pembeli.hasil_validasi import HasilValidasi

if TYPE_CHECKING:
    from models.pembeli.pembeli import Pembeli


class AturanPenjualan:

    def __init__(
        self,
        id_aturan,
        kode_program_komoditas,
        harga_eceran_tertinggi = None,
        batas_maksimal_per_transaksi = None,
        batas_maksimal_per_periode = None,
        periode_kuota = "HARIAN",
        wajib_identitas_nik = False,
        daftar_kategori_pembeli_diizinkan = None,
        status_aktif = True,
    ):
        self.__id_aturan = ""
        self.__kode_program_komoditas = ""
        self.__harga_eceran_tertinggi = None
        self.__batas_maksimal_per_transaksi = None
        self.__batas_maksimal_per_periode = None
        self.__periode_kuota = ""
        self.__wajib_identitas_nik = False
        self.__daftar_kategori_pembeli_diizinkan = []
        self.__status_aktif = False

        self.id_aturan = id_aturan
        self.kode_program_komoditas = kode_program_komoditas
        self.harga_eceran_tertinggi = harga_eceran_tertinggi
        self.batas_maksimal_per_transaksi = batas_maksimal_per_transaksi
        self.batas_maksimal_per_periode = batas_maksimal_per_periode
        self.periode_kuota = periode_kuota
        self.wajib_identitas_nik = wajib_identitas_nik
        self.daftar_kategori_pembeli_diizinkan = (
            daftar_kategori_pembeli_diizinkan if daftar_kategori_pembeli_diizinkan is not None else []
        )
        self.status_aktif = status_aktif

    @property
    def id_aturan(self):
        return self.__id_aturan

    @id_aturan.setter
    def id_aturan(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Aturan harus berupa string non-kosong.")
        self.__id_aturan = value.strip()

    @property
    def kode_program_komoditas(self):
        return self.__kode_program_komoditas

    @kode_program_komoditas.setter
    def kode_program_komoditas(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Kode program komoditas harus berupa string non-kosong.")
        self.__kode_program_komoditas = value.strip().upper()

    @property
    def harga_eceran_tertinggi(self):
        return self.__harga_eceran_tertinggi

    @harga_eceran_tertinggi.setter
    def harga_eceran_tertinggi(self, value):
        if value is not None:
            if not isinstance(value, Decimal):
                try:
                    value = Decimal(str(value))
                except Exception:
                    raise ValueError("Harga eceran tertinggi harus berupa Decimal yang valid.")
            if value <= Decimal("0"):
                raise ValueError("Harga eceran tertinggi harus lebih besar dari 0.")
        self.__harga_eceran_tertinggi = value

    @property
    def batas_maksimal_per_transaksi(self):
        return self.__batas_maksimal_per_transaksi

    @batas_maksimal_per_transaksi.setter
    def batas_maksimal_per_transaksi(self, value):
        if value is not None:
            if not isinstance(value, int) or value <= 0:
                raise ValueError("Batas maksimal per transaksi harus berupa integer positif.")
        self.__batas_maksimal_per_transaksi = value

    @property
    def batas_maksimal_per_periode(self):
        return self.__batas_maksimal_per_periode

    @batas_maksimal_per_periode.setter
    def batas_maksimal_per_periode(self, value):
        if value is not None:
            if not isinstance(value, int) or value <= 0:
                raise ValueError("Batas maksimal per periode harus berupa integer positif.")
        self.__batas_maksimal_per_periode = value

    @property
    def periode_kuota(self):
        return self.__periode_kuota

    @periode_kuota.setter
    def periode_kuota(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Periode kuota harus berupa string non-kosong.")
        self.__periode_kuota = value.strip().upper()

    @property
    def wajib_identitas_nik(self):
        return self.__wajib_identitas_nik

    @wajib_identitas_nik.setter
    def wajib_identitas_nik(self, value):
        if not isinstance(value, bool):
            raise ValueError("wajib_identitas_nik harus bertipe boolean.")
        self.__wajib_identitas_nik = value

    @property
    def daftar_kategori_pembeli_diizinkan(self):
        return list(self.__daftar_kategori_pembeli_diizinkan)

    @daftar_kategori_pembeli_diizinkan.setter
    def daftar_kategori_pembeli_diizinkan(self, value):
        if not isinstance(value, list):
            raise ValueError("daftar_kategori_pembeli_diizinkan harus berupa list.")
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("Setiap elemen kategori pembeli harus berupa string non-kosong.")
        self.__daftar_kategori_pembeli_diizinkan = [item.strip().upper() for item in value]

    @property
    def status_aktif(self):
        return self.__status_aktif

    @status_aktif.setter
    def status_aktif(self, value):
        if not isinstance(value, bool):
            raise ValueError("status_aktif harus bertipe boolean.")
        self.__status_aktif = value

    def validasi_kelayakan_pembeli(self, pembeli: Pembeli):
        """Memvalidasi identitas dan kualifikasi pembeli terhadap aturan komoditas."""
        from models.pembeli.pembeli import Pembeli
        if not isinstance(pembeli, Pembeli):
            raise ValueError("pembeli harus merupakan instance dari kelas Pembeli.")

        if self.wajib_identitas_nik and not pembeli.memiliki_identitas_valid():
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_NIK_REQUIRED",
                pesan_validasi=(
                    f"Komoditas '{self.kode_program_komoditas}' mewajibkan identitas NIK yang valid."
                ),
            )

        if self.daftar_kategori_pembeli_diizinkan:
            kategori_pembeli = pembeli.dapatkan_kategori_pada_program(self.kode_program_komoditas)
            if (
                kategori_pembeli is None
                or kategori_pembeli not in self.daftar_kategori_pembeli_diizinkan
            ):
                return HasilValidasi(
                    status_valid=False,
                    kode_status="ERR_KATEGORI_TIDAK_SESUAI",
                    pesan_validasi=(
                        f"Pembeli tidak memenuhi kategori sasaran untuk {self.kode_program_komoditas}. "
                        f"Kategori diperlukan: {self.daftar_kategori_pembeli_diizinkan}, dimiliki: {kategori_pembeli}."
                    ),
                )

        return HasilValidasi(
            status_valid=True,
            kode_status="OK_KELAYAKAN",
            pesan_validasi=f"Pembeli layak untuk membeli komoditas {self.kode_program_komoditas}.",
        )

    def validasi_kuantitas_pembelian(
        self, jumlah_diminta, akumulasi_periode = 0
    ):
        """Memvalidasi batas maksimal kuantitas pembelian per transaksi maupun akumulasi periode."""
        if not isinstance(jumlah_diminta, int) or jumlah_diminta <= 0:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_QTY_INVALID",
                pesan_validasi=f"Jumlah diminta harus berupa integer positif (diberikan: {jumlah_diminta}).",
            )
        if not isinstance(akumulasi_periode, int) or akumulasi_periode < 0:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_AKUMULASI_INVALID",
                pesan_validasi="Akumulasi periode harus berupa integer non-negatif.",
            )

        if (
            self.batas_maksimal_per_transaksi is not None
            and jumlah_diminta > self.batas_maksimal_per_transaksi
        ):
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_MAX_TRANSAKSI",
                pesan_validasi=(
                    f"Jumlah permintaan ({jumlah_diminta}) melampaui batas maksimal per transaksi "
                    f"({self.batas_maksimal_per_transaksi}) untuk komoditas {self.kode_program_komoditas}."
                ),
            )

        if self.batas_maksimal_per_periode is not None:
            total_setelah = akumulasi_periode + jumlah_diminta
            if total_setelah > self.batas_maksimal_per_periode:
                return HasilValidasi(
                    status_valid=False,
                    kode_status="ERR_MAX_PERIODE",
                    pesan_validasi=(
                        f"Total akumulasi ({total_setelah}) melampaui batas kuota periode "
                        f"({self.batas_maksimal_per_periode}) untuk komoditas {self.kode_program_komoditas}."
                    ),
                )

        return HasilValidasi(
            status_valid=True,
            kode_status="OK_KUANTITAS",
            pesan_validasi="Kuantitas pembelian memenuhi batasan kuota.",
        )

    def hitung_harga_jual_komoditas(self, harga_dasar_barang: Decimal):
        if not isinstance(harga_dasar_barang, Decimal):
            harga_dasar_barang = Decimal(str(harga_dasar_barang))
        if self.harga_eceran_tertinggi is not None:
            return min(harga_dasar_barang, self.harga_eceran_tertinggi)
        return harga_dasar_barang
