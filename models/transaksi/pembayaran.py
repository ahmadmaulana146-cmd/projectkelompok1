from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional


class Pembayaran:
    """Kelas domain untuk mencatat dan memproses transaksi pelunasan pembayaran serta kembalian (FR-12)."""

    def __init__(
        self,
        id_pembayaran: str,
        nominal_tagihan: Decimal,
        nominal_dibayar: Decimal,
        metode_pembayaran: str = "TUNAI",
        waktu_pembayaran: Optional[datetime] = None,
        nominal_kembalian: Decimal = Decimal("0"),
        status_lunas: bool = False,
    ) -> None:
        self.__id_pembayaran: str = ""
        self.__waktu_pembayaran: datetime = datetime.now()
        self.__metode_pembayaran: str = ""
        self.__nominal_tagihan: Decimal = Decimal("0")
        self.__nominal_dibayar: Decimal = Decimal("0")
        self.__nominal_kembalian: Decimal = Decimal("0")
        self.__status_lunas: bool = False

        self.id_pembayaran = id_pembayaran
        self.waktu_pembayaran = (
            waktu_pembayaran if waktu_pembayaran is not None else datetime.now()
        )
        self.metode_pembayaran = metode_pembayaran
        self.nominal_tagihan = nominal_tagihan
        self.nominal_dibayar = nominal_dibayar
        self.nominal_kembalian = nominal_kembalian
        self.status_lunas = status_lunas

    @property
    def id_pembayaran(self) -> str:
        return self.__id_pembayaran

    @id_pembayaran.setter
    def id_pembayaran(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID Pembayaran harus berupa string non-kosong.")
        self.__id_pembayaran = value.strip()

    @property
    def waktu_pembayaran(self) -> datetime:
        return self.__waktu_pembayaran

    @waktu_pembayaran.setter
    def waktu_pembayaran(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise ValueError("Waktu pembayaran harus bertipe datetime.")
        self.__waktu_pembayaran = value

    @property
    def metode_pembayaran(self) -> str:
        return self.__metode_pembayaran

    @metode_pembayaran.setter
    def metode_pembayaran(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Metode pembayaran harus berupa string non-kosong.")
        self.__metode_pembayaran = value.strip().upper()

    @property
    def nominal_tagihan(self) -> Decimal:
        return self.__nominal_tagihan

    @nominal_tagihan.setter
    def nominal_tagihan(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except Exception:
                raise ValueError("Nominal tagihan harus berupa Decimal yang valid.")
        if value < Decimal("0"):
            raise ValueError("Nominal tagihan tidak boleh bernilai negatif.")
        self.__nominal_tagihan = value

    @property
    def nominal_dibayar(self) -> Decimal:
        return self.__nominal_dibayar

    @nominal_dibayar.setter
    def nominal_dibayar(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except Exception:
                raise ValueError("Nominal dibayar harus berupa Decimal yang valid.")
        if value < Decimal("0"):
            raise ValueError("Nominal dibayar tidak boleh bernilai negatif.")
        self.__nominal_dibayar = value

    @property
    def nominal_kembalian(self) -> Decimal:
        return self.__nominal_kembalian

    @nominal_kembalian.setter
    def nominal_kembalian(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except Exception:
                raise ValueError("Nominal kembalian harus berupa Decimal yang valid.")
        if value < Decimal("0"):
            raise ValueError("Nominal kembalian tidak boleh bernilai negatif.")
        self.__nominal_kembalian = value

    @property
    def status_lunas(self) -> bool:
        return self.__status_lunas

    @status_lunas.setter
    def status_lunas(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("status_lunas harus bertipe boolean.")
        self.__status_lunas = value

    def validasi_kecukupan_dana(self) -> bool:
        """Memeriksa apakah uang yang dibayarkan mencukupi nominal total tagihan."""
        return self.nominal_dibayar >= self.nominal_tagihan

    def hitung_kembalian(self) -> Decimal:
        """Menghitung uang kembalian dan menandai pembayaran sebagai lunas."""
        if not self.validasi_kecukupan_dana():
            raise ValueError(
                f"Nominal pembayaran (Rp {self.nominal_dibayar}) kurang dari total tagihan "
                f"(Rp {self.nominal_tagihan})."
            )
        self.nominal_kembalian = self.nominal_dibayar - self.nominal_tagihan
        self.status_lunas = True
        return self.nominal_kembalian
