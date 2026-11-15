from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from models.inventaris.barang import Barang
from models.inventaris.supplier import Supplier
from models.persediaan.aktivitas_persediaan import AktivitasPersediaan
from models.pembeli.hasil_validasi import HasilValidasi

if TYPE_CHECKING:
    from models.pengguna.petugas_gudang import PetugasGudang


class BarangMasuk(AktivitasPersediaan):
    """Subclass AktivitasPersediaan untuk pencatatan pasokan barang masuk dari supplier."""

    def __init__(
        self,
        id_aktivitas: str,
        barang: Barang,
        petugas: PetugasGudang,
        jumlah_perubahan: int,
        catatan: str,
        supplier: Supplier,
        nomor_referensi_surat_jalan: str,
        harga_beli_satuan: Decimal,
        waktu_aktivitas: Optional[datetime] = None,
    ) -> None:
        super().__init__(
            id_aktivitas=id_aktivitas,
            barang=barang,
            petugas=petugas,
            jumlah_perubahan=jumlah_perubahan,
            catatan=catatan,
            waktu_aktivitas=waktu_aktivitas,
        )
        self.__supplier: Optional[Supplier] = None
        self.__nomor_referensi_surat_jalan: str = ""
        self.__harga_beli_satuan: Decimal = Decimal("0")

        self.supplier = supplier
        self.nomor_referensi_surat_jalan = nomor_referensi_surat_jalan
        self.harga_beli_satuan = harga_beli_satuan

    @property
    def supplier(self) -> Supplier:
        if self.__supplier is None:
            raise ValueError("Supplier belum ditentukan.")
        return self.__supplier

    @supplier.setter
    def supplier(self, value: Supplier) -> None:
        if not isinstance(value, Supplier):
            raise ValueError("supplier harus merupakan instance dari kelas Supplier.")
        self.__supplier = value

    @property
    def nomor_referensi_surat_jalan(self) -> str:
        return self.__nomor_referensi_surat_jalan

    @nomor_referensi_surat_jalan.setter
    def nomor_referensi_surat_jalan(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nomor referensi surat jalan harus berupa string non-kosong.")
        self.__nomor_referensi_surat_jalan = value.strip()

    @property
    def harga_beli_satuan(self) -> Decimal:
        return self.__harga_beli_satuan

    @harga_beli_satuan.setter
    def harga_beli_satuan(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except Exception:
                raise ValueError("Harga beli satuan harus berupa Decimal yang valid.")
        if value <= Decimal("0"):
            raise ValueError("Harga beli satuan harus lebih besar dari 0.")
        self.__harga_beli_satuan = value

    def validasi_aktivitas(self) -> HasilValidasi:
        """Memvalidasi bahwa kuantitas penambahan > 0, supplier terisi, dan dokumen sah."""
        if self._jumlah_perubahan <= 0:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_QTY_INVALID",
                pesan_validasi=f"Jumlah barang masuk harus lebih dari 0 (diberikan: {self._jumlah_perubahan}).",
            )
        if self.__supplier is None:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_SUPPLIER_EMPTY",
                pesan_validasi="Data supplier pemasok wajib disertakan.",
            )
        if not self.__nomor_referensi_surat_jalan:
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_NO_REF_EMPTY",
                pesan_validasi="Nomor referensi surat jalan penerimaan wajib disertakan.",
            )
        return HasilValidasi(
            status_valid=True,
            kode_status="OK_BARANG_MASUK",
            pesan_validasi="Dokumen dan kuantitas barang masuk valid.",
        )

    def terapkan_perubahan_stok(self) -> None:
        """Menerapkan penambahan stok ke objek Barang (BR-03)."""
        self._barang.tambah_stok(
            self._jumlah_perubahan,
            sumber=f"Surat Jalan: {self.__nomor_referensi_surat_jalan}",
        )
