from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING

from models.inventaris.barang import Barang
from models.pembeli.hasil_validasi import HasilValidasi
from models.pembeli.pembeli import Pembeli
from models.transaksi.detail_transaksi import DetailTransaksi
from models.transaksi.pembayaran import Pembayaran

if TYPE_CHECKING:
    from models.pengguna.kasir import Kasir


class TransaksiPenjualan:
    """Mengelola keranjang DetailTransaksi, validasi kuota komoditas, dan pemrosesan pembayaran kasir."""

    def __init__(
        self,
        nomor_transaksi: str,
        kasir: Kasir,
        pembeli: Pembeli,
        waktu_transaksi: Optional[datetime] = None,
        daftar_detail: Optional[List[DetailTransaksi]] = None,
        pembayaran: Optional[Pembayaran] = None,
        status_transaksi: str = "DRAFT",
        total_tagihan: Decimal = Decimal("0"),
        catatan_penolakan: Optional[str] = None,
    ) -> None:
        self.__nomor_transaksi: str = ""
        self.__waktu_transaksi: datetime = datetime.now()
        self.__kasir: Optional[Kasir] = None
        self.__pembeli: Optional[Pembeli] = None
        self.__daftar_detail: List[DetailTransaksi] = []
        self.__pembayaran: Optional[Pembayaran] = None
        self.__status_transaksi: str = "DRAFT"
        self.__total_tagihan: Decimal = Decimal("0")
        self.__catatan_penolakan: Optional[str] = None

        self.nomor_transaksi = nomor_transaksi
        self.waktu_transaksi = (
            waktu_transaksi if waktu_transaksi is not None else datetime.now()
        )
        self.kasir = kasir
        self.pembeli = pembeli
        self.daftar_detail = daftar_detail if daftar_detail is not None else []
        self.pembayaran = pembayaran
        self.status_transaksi = status_transaksi
        self.total_tagihan = total_tagihan
        self.catatan_penolakan = catatan_penolakan

    @property
    def nomor_transaksi(self) -> str:
        return self.__nomor_transaksi

    @nomor_transaksi.setter
    def nomor_transaksi(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nomor transaksi harus berupa string non-kosong.")
        self.__nomor_transaksi = value.strip()

    @property
    def waktu_transaksi(self) -> datetime:
        return self.__waktu_transaksi

    @waktu_transaksi.setter
    def waktu_transaksi(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise ValueError("Waktu transaksi harus bertipe datetime.")
        self.__waktu_transaksi = value

    @property
    def kasir(self) -> Kasir:
        if self.__kasir is None:
            raise ValueError("Kasir belum diinisialisasi.")
        return self.__kasir

    @kasir.setter
    def kasir(self, value: Kasir) -> None:
        from models.pengguna.kasir import Kasir
        if not isinstance(value, Kasir):
            raise ValueError("kasir harus merupakan instance dari kelas Kasir.")
        self.__kasir = value

    @property
    def pembeli(self) -> Pembeli:
        if self.__pembeli is None:
            raise ValueError("Pembeli belum diinisialisasi.")
        return self.__pembeli

    @pembeli.setter
    def pembeli(self, value: Pembeli) -> None:
        if not isinstance(value, Pembeli):
            raise ValueError("pembeli harus merupakan instance dari kelas Pembeli.")
        self.__pembeli = value

    @property
    def daftar_detail(self) -> List[DetailTransaksi]:
        return list(self.__daftar_detail)

    @daftar_detail.setter
    def daftar_detail(self, value: List[DetailTransaksi]) -> None:
        if not isinstance(value, list):
            raise ValueError("daftar_detail harus berupa list.")
        for item in value:
            if not isinstance(item, DetailTransaksi):
                raise ValueError("Setiap elemen daftar_detail harus merupakan instance DetailTransaksi.")
        self.__daftar_detail = list(value)

    @property
    def pembayaran(self) -> Optional[Pembayaran]:
        return self.__pembayaran

    @pembayaran.setter
    def pembayaran(self, value: Optional[Pembayaran]) -> None:
        if value is not None and not isinstance(value, Pembayaran):
            raise ValueError("pembayaran harus merupakan instance dari kelas Pembayaran.")
        self.__pembayaran = value

    @property
    def status_transaksi(self) -> str:
        return self.__status_transaksi

    @status_transaksi.setter
    def status_transaksi(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Status transaksi harus berupa string non-kosong.")
        status_valid = {"DRAFT", "SELESAI", "DIBATALKAN", "DITOLAK"}
        status_bersih = value.strip().upper()
        if status_bersih not in status_valid:
            raise ValueError(f"Status transaksi '{value}' tidak valid. Pilihan: {sorted(status_valid)}")
        self.__status_transaksi = status_bersih

    @property
    def total_tagihan(self) -> Decimal:
        return self.__total_tagihan

    @total_tagihan.setter
    def total_tagihan(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except Exception:
                raise ValueError("Total tagihan harus berupa Decimal yang valid.")
        if value < Decimal("0"):
            raise ValueError("Total tagihan tidak boleh negatif.")
        self.__total_tagihan = value

    @property
    def catatan_penolakan(self) -> Optional[str]:
        return self.__catatan_penolakan

    @catatan_penolakan.setter
    def catatan_penolakan(self, value: Optional[str]) -> None:
        if value is not None and not isinstance(value, str):
            raise ValueError("Catatan penolakan harus berupa string atau None.")
        self.__catatan_penolakan = value.strip() if value else None

    def tambah_item_barang(
        self, barang: Barang, jumlah: int, akumulasi_periode: int = 0
    ) -> HasilValidasi:
        """Menambahkan item ke keranjang belanja dengan evaluasi stok dan aturan komoditas 10 langkah (BR-06, BR-13, BR-14, BR-16)."""
        if self.status_transaksi != "DRAFT":
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_STATUS_INVALID",
                pesan_validasi=f"Tidak dapat menambahkan barang pada transaksi dengan status '{self.status_transaksi}'.",
            )

        if not barang.apakah_stok_mencukupi(jumlah):
            pesan = (
                f"Stok barang '{barang.nama_barang}' tidak mencukupi "
                f"(tersedia: {barang.stok_tersedia}, diminta: {jumlah})."
            )
            self.catatan_penolakan = pesan
            return HasilValidasi(
                status_valid=False,
                kode_status="ERR_STOK_KURANG",
                pesan_validasi=pesan,
            )

        aturan = barang.aturan_penjualan
        if aturan is not None and aturan.status_aktif:
            hasil_kelayakan = aturan.validasi_kelayakan_pembeli(self.pembeli)
            if not hasil_kelayakan.apakah_lolos():
                self.catatan_penolakan = hasil_kelayakan.pesan_validasi
                return hasil_kelayakan

            hasil_kuantitas = aturan.validasi_kuantitas_pembelian(
                jumlah_diminta=jumlah, akumulasi_periode=akumulasi_periode
            )
            if not hasil_kuantitas.apakah_lolos():
                self.catatan_penolakan = hasil_kuantitas.pesan_validasi
                return hasil_kuantitas

            harga_satuan = aturan.hitung_harga_jual_komoditas(barang.harga_dasar)
            kode_aturan = aturan.kode_program_komoditas
        else:
            harga_satuan = barang.harga_dasar
            kode_aturan = None

        id_det = f"DET-{uuid.uuid4().hex[:6].upper()}"
        detail = DetailTransaksi(
            id_detail=id_det,
            barang=barang,
            jumlah_beli=jumlah,
            harga_satuan_saat_transaksi=harga_satuan,
            kode_aturan_diterapkan=kode_aturan,
        )
        self.__daftar_detail.append(detail)
        self.hitung_total_pembayaran()

        return HasilValidasi(
            status_valid=True,
            kode_status="OK_ITEM_DITAMBAHKAN",
            pesan_validasi=f"Berhasil menambahkan {jumlah} {barang.satuan} {barang.nama_barang} ke transaksi.",
        )

    def hapus_item_barang(self, kode_barang: str) -> bool:
        """Menghapus item dari keranjang transaksi berdasarkan kode barang."""
        if self.status_transaksi != "DRAFT":
            raise ValueError("Hanya transaksi berstatus DRAFT yang dapat dimodifikasi.")
        item_ditemukan = False
        sisa_detail: List[DetailTransaksi] = []
        for d in self.__daftar_detail:
            if d.barang.kode_barang == kode_barang.strip():
                item_ditemukan = True
            else:
                sisa_detail.append(d)
        if item_ditemukan:
            self.__daftar_detail = sisa_detail
            self.hitung_total_pembayaran()
            return True
        return False

    def hitung_total_pembayaran(self) -> Decimal:
        """Menghitung akumulasi seluruh subtotal item pada keranjang belanja."""
        total = Decimal("0")
        for detail in self.__daftar_detail:
            total += detail.hitung_subtotal()
        self.total_tagihan = total
        return self.total_tagihan

    def proses_pembayaran(self, nominal_bayar: Decimal, metode: str = "TUNAI") -> Pembayaran:
        """Membuat dan memvalidasi pembayaran berdasarkan total tagihan transaksi."""
        if len(self.__daftar_detail) == 0:
            raise ValueError("Transaksi belum memiliki item barang belanjaan (BR-08).")
        self.hitung_total_pembayaran()

        id_byr = f"PAY-{uuid.uuid4().hex[:6].upper()}"
        bayar = Pembayaran(
            id_pembayaran=id_byr,
            nominal_tagihan=self.total_tagihan,
            nominal_dibayar=nominal_bayar,
            metode_pembayaran=metode,
        )
        bayar.hitung_kembalian()
        self.pembayaran = bayar
        return bayar

    def selesaikan_transaksi(self) -> bool:
        """Menyelesaikan transaksi dan melakukan pemotongan stok barang secara atomik (BR-05)."""
        if self.status_transaksi != "DRAFT":
            raise ValueError(f"Transaksi berstatus '{self.status_transaksi}' tidak dapat diselesaikan.")
        if len(self.__daftar_detail) == 0:
            raise ValueError("Satu transaksi penjualan harus memuat minimal satu detail barang (BR-08).")
        if self.pembayaran is None or not self.pembayaran.status_lunas:
            raise ValueError("Transaksi belum dibayar atau pembayaran belum lunas.")

        # Validasi ulang stok seluruh item sebelum pemotongan atomik
        for detail in self.__daftar_detail:
            if not detail.barang.apakah_stok_mencukupi(detail.jumlah_beli):
                self.status_transaksi = "DITOLAK"
                self.catatan_penolakan = (
                    f"Gagal saat finalisasi: Stok barang '{detail.barang.nama_barang}' "
                    f"tidak mencukupi ({detail.barang.stok_tersedia} < {detail.jumlah_beli})."
                )
                raise ValueError(self.catatan_penolakan)

        # Pemotongan stok barang secara atomik
        for detail in self.__daftar_detail:
            detail.barang.kurangi_stok(
                detail.jumlah_beli,
                sumber=f"Penjualan Kasir - No Transaksi: {self.nomor_transaksi}",
            )

        self.status_transaksi = "SELESAI"
        return True

    def batalkan_transaksi(self, alasan: str) -> None:
        """Membatalkan transaksi penjualan dengan mencatat alasan penolakan/pembatalan."""
        if not isinstance(alasan, str) or not alasan.strip():
            raise ValueError("Alasan pembatalan transaksi wajib diisi.")
        self.status_transaksi = "DIBATALKAN"
        self.catatan_penolakan = alasan.strip()
