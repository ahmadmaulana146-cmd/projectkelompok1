from __future__ import annotations
from datetime import datetime
from typing import Optional


class HasilValidasi:
 
    def __init__(
        self,
        status_valid,
        kode_status,
        pesan_validasi,
        waktu_evaluasi = None,
    ):
        if not isinstance(status_valid, bool):
            raise ValueError("status_valid harus bertipe boolean.")
        if not isinstance(kode_status, str) or not kode_status.strip():
            raise ValueError("kode_status harus berupa string non-kosong.")
        if not isinstance(pesan_validasi, str) or not pesan_validasi.strip():
            raise ValueError("pesan_validasi harus berupa string non-kosong.")

        self.status_valid = status_valid
        self.kode_status = kode_status.strip()
        self.pesan_validasi = pesan_validasi.strip()
        self.waktu_evaluasi: datetime = (
            waktu_evaluasi if waktu_evaluasi is not None else datetime.now()
        )

    def apakah_lolos(self):
        return self.status_valid

    def format_pesan_audit(self):
        """Menyusun representasi teks terstruktur untuk catatan audit sistem."""
        status_teks = "LOLOS" if self.status_valid else "DITOLAK"
        timestamp = self.waktu_evaluasi.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{self.kode_status}] {self.pesan_validasi} (Status: {status_teks})"

    def __str__(self):
        return self.format_pesan_audit()
