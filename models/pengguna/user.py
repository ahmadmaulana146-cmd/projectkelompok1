from __future__ import annotations
from abc import ABC, abstractmethod
import hashlib
from typing import List


class User(ABC):
    def __init__(
        self,
        id_user,
        username,
        password_hash,
        nama_lengkap,
        peran,
        status_aktif = True,
    ):
        self.__id_user = ""
        self.__username = ""
        self.__password_hash = ""
        self.__nama_lengkap = ""
        self.__peran = ""
        self.__status_aktif = False

        self.id_user = id_user
        self.username = username
        self.password_hash = password_hash
        self.nama_lengkap = nama_lengkap
        self.peran = peran
        self.status_aktif = status_aktif

    @staticmethod
    def hash_password(plain_password):
        """Membuat SHA-256 hash dari kata sandi polos."""
        if not isinstance(plain_password, str) or not plain_password.strip():
            raise ValueError("Password tidak boleh kosong.")
        return hashlib.sha256(plain_password.strip().encode("utf-8")).hexdigest()

    @property
    def id_user(self):
        return self.__id_user

    @id_user.setter
    def id_user(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("ID User harus berupa string non-kosong.")
        self.__id_user = value.strip()

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Username harus berupa string non-kosong.")
        if len(value.strip()) < 3:
            raise ValueError("Username minimal harus terdiri dari 3 karakter.")
        self.__username = value.strip()

    @property
    def password_hash(self):
        return self.__password_hash

    @password_hash.setter
    def password_hash(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Password hash harus berupa string non-kosong.")
        self.__password_hash = value.strip()

    @property
    def nama_lengkap(self):
        return self.__nama_lengkap

    @nama_lengkap.setter
    def nama_lengkap(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Nama lengkap harus berupa string non-kosong.")
        self.__nama_lengkap = value.strip()

    @property
    def peran(self):
        return self.__peran

    @peran.setter
    def peran(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Peran harus berupa string non-kosong.")
        self.__peran = value.strip()

    @property
    def status_aktif(self) -> bool:
        return self.__status_aktif

    @status_aktif.setter
    def status_aktif(self, value):
        if not isinstance(value, bool):
            raise ValueError("Status aktif harus bertipe boolean.")
        self.__status_aktif = value

    def login(self, username, password) -> bool:
        """Memverifikasi username, password, dan status aktif untuk proses masuk sistem."""
        if not self.status_aktif:
            return False
        if self.username != username.strip():
            return False
        return self.verifikasi_password(password)

    def logout(self) -> bool:
        """Melakukan terminasi sesi pengguna."""
        return True

    def verifikasi_password(self, password_plain) -> bool:
        """Memeriksa kesesuaian kata sandi polos terhadap hash tersimpan."""
        if not isinstance(password_plain, str) or not password_plain.strip():
            return False
        return self.hash_password(password_plain) == self.password_hash

    def ubah_password(self, password_lama, password_baru) -> bool:
        """Mengubah kata sandi setelah memverifikasi kata sandi lama."""
        if not self.verifikasi_password(password_lama):
            raise ValueError("Kata sandi lama tidak sesuai.")
        if len(password_baru.strip()) < 6:
            raise ValueError("Kata sandi baru minimal harus 6 karakter.")
        self.password_hash = self.hash_password(password_baru)
        return True

    @abstractmethod
    def dapatkan_hak_akses(self) -> List[str]:
        """Mengembalikan daftar hak akses yang dimiliki oleh peran pengguna."""
        raise NotImplementedError
