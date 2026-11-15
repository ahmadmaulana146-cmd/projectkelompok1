from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from models.inventaris.barang import Barang
from models.persediaan.aktivitas_persediaan import AktivitasPersediaan
from models.transaksi.transaksi_penjualan import TransaksiPenjualan


class LayananLaporan:
    """Menyediakan fasilitas pelaporan penjualan, evaluasi posisi stok inventaris, dan pencarian jejak audit."""

    def __init__(
        self,
        daftar_transaksi: Optional[List[TransaksiPenjualan]] = None,
        daftar_barang: Optional[List[Barang]] = None,
        daftar_aktivitas: Optional[List[AktivitasPersediaan]] = None,
    ) -> None:
        self.__daftar_transaksi: List[TransaksiPenjualan] = []
        self.__daftar_barang: List[Barang] = []
        self.__daftar_aktivitas: List[AktivitasPersediaan] = []

        self.daftar_transaksi = (
            daftar_transaksi if daftar_transaksi is not None else []
        )
        self.daftar_barang = (
            daftar_barang if daftar_barang is not None else []
        )
        self.daftar_aktivitas = (
            daftar_aktivitas if daftar_aktivitas is not None else []
        )

    @property
    def daftar_transaksi(self) -> List[TransaksiPenjualan]:
        return list(self.__daftar_transaksi)

    @daftar_transaksi.setter
    def daftar_transaksi(self, value: List[TransaksiPenjualan]) -> None:
        if not isinstance(value, list):
            raise ValueError("daftar_transaksi harus berupa list.")
        for item in value:
            if not isinstance(item, TransaksiPenjualan):
                raise ValueError("Elemen daftar_transaksi harus merupakan instance TransaksiPenjualan.")
        self.__daftar_transaksi = list(value)

    @property
    def daftar_barang(self) -> List[Barang]:
        return list(self.__daftar_barang)

    @daftar_barang.setter
    def daftar_barang(self, value: List[Barang]) -> None:
        if not isinstance(value, list):
            raise ValueError("daftar_barang harus berupa list.")
        for item in value:
            if not isinstance(item, Barang):
                raise ValueError("Elemen daftar_barang harus merupakan instance Barang.")
        self.__daftar_barang = list(value)

    @property
    def daftar_aktivitas(self) -> List[AktivitasPersediaan]:
        return list(self.__daftar_aktivitas)

    @daftar_aktivitas.setter
    def daftar_aktivitas(self, value: List[AktivitasPersediaan]) -> None:
        if not isinstance(value, list):
            raise ValueError("daftar_aktivitas harus berupa list.")
        for item in value:
            if not isinstance(item, AktivitasPersediaan):
                raise ValueError("Elemen daftar_aktivitas harus merupakan instance AktivitasPersediaan.")
        self.__daftar_aktivitas = list(value)

    def tambah_transaksi(self, transaksi: TransaksiPenjualan) -> None:
        """Mendaftarkan transaksi ke koleksi laporan."""
        if not isinstance(transaksi, TransaksiPenjualan):
            raise ValueError("transaksi harus berupa objek TransaksiPenjualan.")
        self.__daftar_transaksi.append(transaksi)

    def tambah_barang(self, barang: Barang) -> None:
        """Mendaftarkan barang ke koleksi inventaris."""
        if not isinstance(barang, Barang):
            raise ValueError("barang harus berupa objek Barang.")
        self.__daftar_barang.append(barang)

    def tambah_aktivitas(self, aktivitas: AktivitasPersediaan) -> None:
        """Mendaftarkan aktivitas persediaan ke koleksi jejak audit."""
        if not isinstance(aktivitas, AktivitasPersediaan):
            raise ValueError("aktivitas harus berupa objek AktivitasPersediaan.")
        self.__daftar_aktivitas.append(aktivitas)

    def hasilkan_laporan_penjualan(
        self, periode_awal: date, periode_akhir: date
    ) -> Dict[str, Any]:
        """Menghasilkan rekapitulasi penjualan yang selesai pada rentang tanggal tertentu (FR-14)."""
        if not isinstance(periode_awal, date) or not isinstance(periode_akhir, date):
            raise ValueError("Periode awal dan akhir harus berupa objek date.")
        if periode_awal > periode_akhir:
            raise ValueError("Periode awal tidak boleh lebih besar dari periode akhir.")

        transaksi_terfilter: List[TransaksiPenjualan] = []
        total_omset = Decimal("0")
        total_item_terjual = 0

        for tx in self.__daftar_transaksi:
            tanggal_tx = tx.waktu_transaksi.date()
            if periode_awal <= tanggal_tx <= periode_akhir and tx.status_transaksi == "SELESAI":
                transaksi_terfilter.append(tx)
                total_omset += tx.total_tagihan
                for d in tx.daftar_detail:
                    total_item_terjual += d.jumlah_beli

        return {
            "periode_awal": periode_awal.isoformat(),
            "periode_akhir": periode_akhir.isoformat(),
            "jumlah_transaksi": len(transaksi_terfilter),
            "total_omset": total_omset,
            "total_item_terjual": total_item_terjual,
            "rincian_transaksi": [
                {
                    "nomor_transaksi": tx.nomor_transaksi,
                    "waktu": tx.waktu_transaksi.isoformat(),
                    "kasir": tx.kasir.nama_lengkap,
                    "pembeli": tx.pembeli.nama_pembeli,
                    "total_tagihan": tx.total_tagihan,
                    "jumlah_item": len(tx.daftar_detail),
                }
                for tx in transaksi_terfilter
            ],
        }

    def hasilkan_laporan_persediaan(
        self, hanya_stok_kritis: bool = False
    ) -> List[Dict[str, Any]]:
        """Menghasilkan laporan posisi persediaan saat ini dan peringatan stok minimum (FR-15, FR-16)."""
        hasil: List[Dict[str, Any]] = []
        for b in self.__daftar_barang:
            kritis = b.apakah_mencapai_batas_minimum()
            if hanya_stok_kritis and not kritis:
                continue
            hasil.append({
                "kode_barang": b.kode_barang,
                "nama_barang": b.nama_barang,
                "satuan": b.satuan,
                "kategori": b.kategori.nama_kategori if b.kategori else "-",
                "harga_dasar": b.harga_dasar,
                "harga_berlaku": b.dapatkan_harga_berlaku(),
                "stok_tersedia": b.stok_tersedia,
                "stok_minimum": b.stok_minimum,
                "status_kritis": kritis,
                "status_aktif": b.status_aktif,
            })
        return hasil

    def cari_riwayat_transaksi(
        self, kata_kunci: str, filter_status: Optional[str] = None
    ) -> List[TransaksiPenjualan]:
        """Mencari dan menyaring riwayat transaksi penjualan (FR-17, FR-18)."""
        kunci = kata_kunci.strip().lower()
        filter_st = filter_status.strip().upper() if filter_status else None
        hasil: List[TransaksiPenjualan] = []

        for tx in self.__daftar_transaksi:
            if filter_st and tx.status_transaksi != filter_st:
                continue
            cocok_nomor = kunci in tx.nomor_transaksi.lower()
            cocok_pembeli = kunci in tx.pembeli.nama_pembeli.lower()
            cocok_kasir = kunci in tx.kasir.nama_lengkap.lower()
            if cocok_nomor or cocok_pembeli or cocok_kasir:
                hasil.append(tx)

        return hasil

    def cari_riwayat_persediaan(
        self, kode_barang: Optional[str] = None, jenis: Optional[str] = None
    ) -> List[AktivitasPersediaan]:
        """Mencari dan menyaring riwayat aktivitas persediaan gudang (FR-17, FR-18)."""
        kode = kode_barang.strip().upper() if kode_barang else None
        filter_j = jenis.strip().lower() if jenis else None
        hasil: List[AktivitasPersediaan] = []

        for akt in self.__daftar_aktivitas:
            if kode and akt.barang.kode_barang.upper() != kode:
                continue
            if filter_j and filter_j not in akt.__class__.__name__.lower():
                continue
            hasil.append(akt)

        return hasil
