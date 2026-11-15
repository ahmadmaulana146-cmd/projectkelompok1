from __future__ import annotations
import uuid
from typing import List, Optional, TYPE_CHECKING

from models.pengguna.user import User

if TYPE_CHECKING:
    from models.pembeli.pembeli import Pembeli
    from models.transaksi.transaksi_penjualan import TransaksiPenjualan


class Kasir(User):
    """Subclass User yang merepresentasikan Kasir pelayanan transaksi."""

    def __init__(
        self,
        id_user: str,
        username: str,
        password_hash: str,
        nama_lengkap: str,
        shift_kerja: str,
        status_aktif: bool = True,
    ) -> None:
        super().__init__(
            id_user=id_user,
            username=username,
            password_hash=password_hash,
            nama_lengkap=nama_lengkap,
            peran="Kasir",
            status_aktif=status_aktif,
        )
        self.__shift_kerja: str = ""
        self.shift_kerja = shift_kerja

    @property
    def shift_kerja(self) -> str:
        return self.__shift_kerja

    @shift_kerja.setter
    def shift_kerja(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Shift kerja harus berupa string non-kosong.")
        self.__shift_kerja = value.strip()

    def dapatkan_hak_akses(self) -> List[str]:
        return [
            "buat_transaksi_baru",
            "catat_data_pembeli",
            "proses_pembayaran",
            "lihat_riwayat_penjualan",
        ]

    def buat_transaksi_baru(self, pembeli: Pembeli) -> TransaksiPenjualan:
        from models.pembeli.pembeli import Pembeli
        from models.transaksi.transaksi_penjualan import TransaksiPenjualan
        if not isinstance(pembeli, Pembeli):
            raise ValueError("pembeli harus merupakan instance dari kelas Pembeli.")
        nomor_tx = f"TX-{uuid.uuid4().hex[:8].upper()}"
        return TransaksiPenjualan(nomor_transaksi=nomor_tx, kasir=self, pembeli=pembeli)

    def catat_data_pembeli(
        self, nama: str, nik: Optional[str], alamat: str
    ) -> Pembeli:
        from models.pembeli.pembeli import Pembeli
        id_cust = f"CUST-{uuid.uuid4().hex[:6].upper()}"
        is_umum = (nik is None or len(nik.strip()) == 0)
        return Pembeli(
            id_pembeli=id_cust,
            nama_pembeli=nama,
            nik_terenkripsi=nik,
            alamat_domisili=alamat,
            tipe_pembeli_umum=is_umum,
        )
