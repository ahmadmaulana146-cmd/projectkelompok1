from __future__ import annotations
from datetime import datetime
from typing import Optional


class HasilValidasi:
    """Value Object untuk membawa status kelulusan validasi, kode alasan teknis, dan catatan audit."""

    def __init__(
        self,
        status_valid: bool,
        kode_status: str,
        pesan_validasi: str,
        waktu_evaluasi: Optional[datetime] = None,
    ) -> None:
        if not isinstance(status_valid, bool):
            raise ValueError("status_valid harus bertipe boolean.")
        if not isinstance(kode_status, str) or not kode_status.strip():
            raise ValueError("kode_status harus berupa string non-kosong.")
        if not isinstance(pesan_validasi, str) or not pesan_validasi.strip():
            raise ValueError("pesan_validasi harus berupa string non-kosong.")

        self.status_valid: bool = status_valid
        self.kode_status: str = kode_status.strip()
        self.pesan_validasi: str = pesan_validasi.strip()
        self.waktu_evaluasi: datetime = (
            waktu_evaluasi if waktu_evaluasi is not None else datetime.now()
        )

    def apakah_lolos(self) -> bool:
        """Memeriksa apakah hasil evaluasi validasi berstatus sukses/lolos."""
        return self.status_valid

    def format_pesan_audit(self) -> str:
        """Menyusun representasi teks terstruktur untuk catatan audit sistem."""
        status_teks = "LOLOS" if self.status_valid else "DITOLAK"
        timestamp = self.waktu_evaluasi.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{self.kode_status}] {self.pesan_validasi} (Status: {status_teks})"

    def __str__(self) -> str:
        return self.format_pesan_audit()
