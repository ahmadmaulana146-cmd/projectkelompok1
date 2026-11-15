from __future__ import annotations
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from models.inventaris.kategori import Kategori

if TYPE_CHECKING:
    from models.pembeli.aturan_penjualan import AturanPenjualan


class Barang:

    def __init__(
        self,
        kode_barang,
        nama_barang,
        satuan,
        harga_dasar,
        stok_tersedia = 0,
        stok_minimum = 5,
        status_aktif  = True,
        kategori: Optional[Kategori] = None,
        aturan_penjualan: Optional[AturanPenjualan] = None,
    ) -> None:
        self.__kode_barang = ""
        self.__nama_barang = ""
        self.__satuan = ""
        self.__harga_dasar = Decimal("0")
        self.__stok_tersedia = 0
        self.__stok_minimum = 0
        self.__status_aktif = False
        self.__kategori: Optional[Kategori] = None
        self.__aturan_penjualan: Optional[AturanPenjualan] = None

        self.kode_barang = kode_barang
        self.nama_barang = nama_barang
        self.satuan = satuan
        self.harga_dasar = harga_dasar
        self.stok_tersedia = stok_tersedia
        self.stok_minimum = stok_minimum
        self.status_aktif = status_aktif
        if kategori is not None:
            self.kategori = kategori
        self.aturan_penjualan = aturan_penjualan

    @property
    def kode_barang(self) -> str:
        return self.__kode_barang

    @kode_barang.setter
    def kode_barang(self, value) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Kode barang harus berupa string non-kosong.")
        self.__kode_barang = value.strip()

    @property
    def nama_barang(self) -> str:
        return self.__nama_barang

    @nama_barang.setter
    def nama_barang(self, value) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama barang harus berupa string non-kosong.")
        self.__nama_barang = value.strip()

    @property
    def satuan(self) -> str:
        return self.__satuan

    @satuan.setter
    def satuan(self, value) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Satuan harus berupa string non-kosong.")
        self.__satuan = value.strip()

    @property
    def harga_dasar(self) -> Decimal:
        return self.__harga_dasar

    @harga_dasar.setter
    def harga_dasar(self, value) -> None:
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except Exception:
                raise ValueError("Harga dasar harus berupa objek Decimal yang valid.")
        if value <= Decimal("0"):
            raise ValueError("Harga dasar barang harus lebih besar dari 0.")
        self.__harga_dasar = value

    @property
    def stok_tersedia(self) -> int:
        return self.__stok_tersedia

    @stok_tersedia.setter
    def stok_tersedia(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Stok tersedia harus berupa bilangan bulat (int).")
        if value < 0:
            raise ValueError(f"Stok tersedia tidak boleh negatif (diberikan: {value}).")
        self.__stok_tersedia = value

    @property
    def stok_minimum(self) -> int:
        return self.__stok_minimum

    @stok_minimum.setter
    def stok_minimum(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError("Stok minimum harus berupa bilangan bulat (int).")
        if value < 0:
            raise ValueError("Stok minimum tidak boleh negatif.")
        self.__stok_minimum = value

    @property
    def status_aktif(self) -> bool:
        return self.__status_aktif

    @status_aktif.setter
    def status_aktif(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("Status aktif harus berupa boolean.")
        self.__status_aktif = value

    @property
    def kategori(self) -> Optional[Kategori]:
        return self.__kategori

    @kategori.setter
    def kategori(self, value: Optional[Kategori]) -> None:
        if value is not None and not isinstance(value, Kategori):
            raise ValueError("Kategori harus merupakan instance dari kelas Kategori.")
        self.__kategori = value

    @property
    def aturan_penjualan(self) -> Optional[AturanPenjualan]:
        return self.__aturan_penjualan

    @aturan_penjualan.setter
    def aturan_penjualan(self, value: Optional[AturanPenjualan]) -> None:
        from models.pembeli.aturan_penjualan import AturanPenjualan
        if value is not None and not isinstance(value, AturanPenjualan):
            raise ValueError("Aturan penjualan harus merupakan instance dari AturanPenjualan.")
        self.__aturan_penjualan = value

    def tambah_stok(self, jumlah: int, sumber = "") -> None:
        if not isinstance(jumlah, int) or jumlah <= 0:
            raise ValueError("Jumlah stok yang ditambahkan harus berupa bilangan bulat positif.")
        self.stok_tersedia = self.__stok_tersedia + jumlah

    def kurangi_stok(self, jumlah: int, sumber = "") -> None:
        if not isinstance(jumlah, int) or jumlah <= 0:
            raise ValueError("Jumlah stok yang dikurangkan harus berupa bilangan bulat positif.")
        if self.__stok_tersedia < jumlah:
            raise ValueError(
                f"Stok tidak mencukupi untuk pengurangan {jumlah}. "
                f"Stok saat ini: {self.__stok_tersedia}."
            )
        self.stok_tersedia = self.__stok_tersedia - jumlah

    def sesuaikan_stok_aktual(self, stok_fisik_baru: int, alasan) -> None:
        if not isinstance(stok_fisik_baru, int) or stok_fisik_baru < 0:
            raise ValueError("Stok fisik hasil opname harus berupa bilangan bulat non-negatif.")
        if not isinstance(alasan, str) or not alasan.strip():
            raise ValueError("Alasan penyesuaian stok wajib diisi (BR-10).")
        self.stok_tersedia = stok_fisik_baru

    def apakah_stok_mencukupi(self, jumlah_diminta: int) -> bool:
        if not isinstance(jumlah_diminta, int) or jumlah_diminta <= 0:
            return False
        return self.__stok_tersedia >= jumlah_diminta

    def apakah_mencapai_batas_minimum(self) -> bool:
        return self.__stok_tersedia <= self.__stok_minimum

    def dapatkan_harga_berlaku(self) -> Decimal:
        if self.__aturan_penjualan is not None and self.__aturan_penjualan.status_aktif:
            return self.__aturan_penjualan.hitung_harga_jual_komoditas(self.__harga_dasar)
        return self.__harga_dasar
