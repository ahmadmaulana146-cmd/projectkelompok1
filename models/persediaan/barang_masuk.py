from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING

from models.inventaris.barang import Barang
from models.inventaris.supplier import Supplier
from models.persediaan.aktivitas_persediaan import AktivitasPersediaan

if TYPE_CHECKING:
    from models.pengguna.petugas_gudang import PetugasGudang


class BarangMasuk(AktivitasPersediaan):
    """Subclass AktivitasPersediaan untuk pencatatan pasokan barang masuk (FR-06, BR-03)."""

    PREFIX_ID: str = "IN"

    def __init__(
        self,
        barang: Barang,
        petugas: PetugasGudang,
        supplier: Supplier,
        jumlah_perubahan: int,
        nomor_referensi_surat_jalan: str,
        harga_beli_satuan: Decimal,
        catatan: str = "",
    ) -> None:
       
        self.__supplier: Supplier
        self.__nomor_referensi_surat_jalan: str = ""
        self.__harga_beli_satuan: Decimal = Decimal("0")


        super().__init__(
            barang=barang,
            petugas=petugas,
            jumlah_perubahan=jumlah_perubahan,
            catatan=catatan,
        )

        self.supplier = supplier
        self.nomor_referensi_surat_jalan = nomor_referensi_surat_jalan
        self.harga_beli_satuan = harga_beli_satuan

    @property
    def supplier(self) -> Supplier:
        return self.__supplier

    @supplier.setter
    def supplier(self, value: Supplier) -> None:
        if value is None:
            raise ValueError("Supplier pemasok barang tidak boleh kosong.")
        self.__supplier = value

    @property
    def nomor_referensi_surat_jalan(self) -> str:
        return self.__nomor_referensi_surat_jalan

    @nomor_referensi_surat_jalan.setter
    def nomor_referensi_surat_jalan(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Nomor referensi surat jalan wajib diisi.")
        self.__nomor_referensi_surat_jalan = value.strip()

    @property
    def harga_beli_satuan(self) -> Decimal:
        return self.__harga_beli_satuan

    @harga_beli_satuan.setter
    def harga_beli_satuan(self, value: Decimal) -> None:
        if value < Decimal("0"):
            raise ValueError("Harga beli satuan tidak boleh bernilai negatif.")
        self.__harga_beli_satuan = value

   
    def validasi_aktivitas(self) -> bool:
        """Valid bila jumlah > 0, supplier terisi, nomor surat jalan terisi, dan harga >= 0."""
        if self.jumlah_perubahan <= 0:
            return False
        if self.supplier is None:
            return False
        if not self.nomor_referensi_surat_jalan:
            return False
        if self.harga_beli_satuan < Decimal("0"):
            return False
        return True

    def terapkan_perubahan_stok(self) -> None:
        """Menambahkan stok pada objek Barang (BR-03)."""
        self.barang.tambah_stok(
            jumlah=self.jumlah_perubahan,
            sumber=f"BARANG_MASUK ({self.id_aktivitas})",
        )