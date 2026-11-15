from __future__ import annotations
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from models.inventaris.barang import Barang

if TYPE_CHECKING:
    pass


class DetailTransaksi:
    def __init__(
        self,
        id_detail,
        barang,
        jumlah_beli,
        harga_satuan_saat_transaksi: Decimal,
        kode_aturan_diterapkan: Optional[str] = None,
    ) -> None:
        self.__id_detail = ""
        self.__barang: Optional[Barang] = None
        self.__jumlah_beli: int = 0
        self.__harga_satuan_saat_transaksi: Decimal = Decimal("0")
        self.__subtotal: Decimal = Decimal("0")
        self.__kode_aturan_diterapkan: Optional[str] = None

        self.id_detail = id_detail
        self.barang = barang
        self.jumlah_beli = jumlah_beli
        self.harga_satuan_saat_transaksi = harga_satuan_saat_transaksi
        self.kode_aturan_diterapkan = kode_aturan_diterapkan
        self.hitung_subtotal()

    @property
    def id_detail(self) -> str:
        return self.__id_detail

    @id_detail.setter
    def id_detail(self, value) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Detail harus berupa string non-kosong.")
        self.__id_detail = value.strip()

    @property
    def barang(self) -> Barang:
        if self.__barang is None:
            raise ValueError("Barang belum diinisialisasi.")
        return self.__barang

    @barang.setter
    def barang(self, value) -> None:
        if not isinstance(value, Barang):
            raise ValueError("barang harus merupakan instance dari kelas Barang.")
        self.__barang = value

    @property
    def jumlah_beli(self) -> int:
        return self.__jumlah_beli

    @jumlah_beli.setter
    def jumlah_beli(self, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Jumlah beli harus berupa bilangan bulat positif.")
        self.__jumlah_beli = value

    @property
    def harga_satuan_saat_transaksi(self) -> Decimal:
        return self.__harga_satuan_saat_transaksi

    @harga_satuan_saat_transaksi.setter
    def harga_satuan_saat_transaksi(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except Exception:
                raise ValueError("Harga satuan saat transaksi harus berupa Decimal yang valid.")
        if value <= Decimal("0"):
            raise ValueError("Harga satuan saat transaksi harus lebih besar dari 0.")
        self.__harga_satuan_saat_transaksi = value

    @property
    def subtotal(self) -> Decimal:
        return self.__subtotal

    @subtotal.setter
    def subtotal(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except Exception:
                raise ValueError("Subtotal harus berupa Decimal yang valid.")
        if value < Decimal("0"):
            raise ValueError("Subtotal tidak boleh bernilai negatif.")
        self.__subtotal = value

    @property
    def kode_aturan_diterapkan(self) -> Optional[str]:
        return self.__kode_aturan_diterapkan

    @kode_aturan_diterapkan.setter
    def kode_aturan_diterapkan(self, value: Optional[str]) -> None:
        if value is not None and not isinstance(value, str):
            raise ValueError("Kode aturan diterapkan harus bertipe string atau None.")
        self.__kode_aturan_diterapkan = value.strip() if value else None

    def hitung_subtotal(self) -> Decimal:
        """Menghitung subtotal = jumlah_beli * harga_satuan_saat_transaksi."""
        self.subtotal = Decimal(self.jumlah_beli) * self.harga_satuan_saat_transaksi
        return self.subtotal

    def perbarui_jumlah(self, jumlah_baru: int) -> None:
        """Memperbarui kuantitas pembelian dan mengkalkulasi ulang subtotal."""
        self.jumlah_beli = jumlah_baru
        self.hitung_subtotal()
