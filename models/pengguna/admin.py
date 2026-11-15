from __future__ import annotations
from typing import List, TYPE_CHECKING

from models.pengguna.user import User

if TYPE_CHECKING:
    from models.inventaris.barang import Barang
    from models.inventaris.kategori import Kategori
    from models.inventaris.supplier import Supplier
    from models.pembeli.aturan_penjualan import AturanPenjualan


class Admin(User):
    def __init__(
        self,
        id_user,
        username,
        password_hash,
        nama_lengkap,
        status_aktif = True,
    ) -> None:
        super().__init__(
            id_user=id_user,
            username=username,
            password_hash=password_hash,
            nama_lengkap=nama_lengkap,
            peran="Admin",
            status_aktif=status_aktif,
        )

    def dapatkan_hak_akses(self) -> List[str]:
        return [
            "kelola_pengguna",
            "kelola_barang",
            "kelola_kategori",
            "kelola_supplier",
            "tetapkan_aturan_penjualan",
            "lihat_laporan_penjualan",
            "lihat_laporan_persediaan",
        ]

    def kelola_pengguna(self, data_user: User, aksi):
        if not isinstance(data_user, User):
            raise ValueError("data_user harus merupakan turunan dari kelas User.")
        if not isinstance(aksi, str) or not aksi.strip():
            raise ValueError("Aksi tidak boleh kosong.")
        aksi_valid = {"tambah", "ubah", "hapus", "aktifkan", "nonaktifkan"}
        aksi_bersih = aksi.strip().lower()
        if aksi_bersih not in aksi_valid:
            raise ValueError(f"Aksi '{aksi}' tidak valid. Pilihan aksi: {sorted(aksi_valid)}")
        if aksi_bersih == "aktifkan":
            data_user.status_aktif = True
        elif aksi_bersih == "nonaktifkan":
            data_user.status_aktif = False
        return True

    def kelola_barang(self, barang: Barang, aksi):
        from models.inventaris.barang import Barang
        if not isinstance(barang, Barang):
            raise ValueError("barang harus merupakan instance dari kelas Barang.")
        if not isinstance(aksi, str) or not aksi.strip():
            raise ValueError("Aksi tidak boleh kosong.")
        aksi_valid = {"tambah", "ubah", "hapus", "aktifkan", "nonaktifkan"}
        aksi_bersih = aksi.strip().lower()
        if aksi_bersih not in aksi_valid:
            raise ValueError(f"Aksi '{aksi}' tidak valid. Pilihan aksi: {sorted(aksi_valid)}")
        if aksi_bersih == "aktifkan":
            barang.status_aktif = True
        elif aksi_bersih == "nonaktifkan":
            barang.status_aktif = False
        return True

    def kelola_kategori(self, kategori: Kategori, aksi):
        from models.inventaris.kategori import Kategori
        if not isinstance(kategori, Kategori):
            raise ValueError("kategori harus merupakan instance dari kelas Kategori.")
        if not isinstance(aksi, str) or not aksi.strip():
            raise ValueError("Aksi tidak boleh kosong.")
        aksi_valid = {"tambah", "ubah", "hapus"}
        aksi_bersih = aksi.strip().lower()
        if aksi_bersih not in aksi_valid:
            raise ValueError(f"Aksi '{aksi}' tidak valid. Pilihan aksi: {sorted(aksi_valid)}")
        return True

    def kelola_supplier(self, supplier: Supplier, aksi):
        from models.inventaris.supplier import Supplier
        if not isinstance(supplier, Supplier):
            raise ValueError("supplier harus merupakan instance dari kelas Supplier.")
        if not isinstance(aksi, str) or not aksi.strip():
            raise ValueError("Aksi tidak boleh kosong.")
        aksi_valid = {"tambah", "ubah", "hapus"}
        aksi_bersih = aksi.strip().lower()
        if aksi_bersih not in aksi_valid:
            raise ValueError(f"Aksi '{aksi}' tidak valid. Pilihan aksi: {sorted(aksi_valid)}")
        return True

    def tetapkan_aturan_penjualan(
        self, barang: Barang, aturan: AturanPenjualan
    ):
        from models.inventaris.barang import Barang
        from models.pembeli.aturan_penjualan import AturanPenjualan
        if not isinstance(barang, Barang):
            raise ValueError("barang harus merupakan instance dari kelas Barang.")
        if not isinstance(aturan, AturanPenjualan):
            raise ValueError("aturan harus merupakan instance dari kelas AturanPenjualan.")
        barang.aturan_penjualan = aturan
        return True
