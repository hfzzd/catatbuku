"""Riwayat sesi baca CatatBuku.

Setiap kali progres sebuah buku maju (lewat perintah ``progres``),
satu sesi dicatat di berkas ``sesi.json`` (di samping berkas data buku,
jadi ikut terisolasi oleh env CATATBUKU_DATA saat test).

Satu sesi adalah dict:
    {
        "tanggal": "YYYY-MM-DD",
        "judul": str,          # judul buku, supaya tetap terbaca walau
                               # buku dihapus / nomor urut berubah
        "dari": int,           # halaman sebelum sesi
        "ke": int,             # halaman sesudah sesi
        "dibaca": int,         # ke - dari (halaman yang dibaca sesi ini)
    }

Hanya progres maju yang dicatat; memundurkan halaman bukan sesi baca.
"""

import json
import os
from datetime import date

from .buku import CatatBukuError, berkas_data


def berkas_sesi(path_buku=None):
    """Lokasi berkas sesi (sesi.json di samping berkas data buku)."""
    buku = path_buku or berkas_data()
    return os.path.join(os.path.dirname(buku), "sesi.json")


def muat_sesi(path=None):
    """Muat daftar sesi; [] bila berkas belum ada."""
    path = path or berkas_sesi()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError) as exc:
        raise CatatBukuError(
            f"Berkas sesi {path} tidak bisa dibaca ({exc}). "
            "Periksa berkasnya atau hapus lalu mulai lagi."
        ) from exc
    if not isinstance(data, list):
        raise CatatBukuError(
            f"Berkas sesi {path} formatnya salah (harusnya berisi daftar sesi)."
        )
    return data


def simpan_sesi(daftar, path=None):
    """Simpan daftar sesi ke berkas JSON."""
    path = path or berkas_sesi()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(daftar, f, ensure_ascii=False, indent=2)
        f.write("\n")


def catat_sesi(daftar, buku, dari, ke, tanggal=None):
    """Catat satu sesi baca; kembalikan sesi, atau None bila tak dicatat.

    Tidak dicatat bila halaman tidak maju (ke <= dari).
    """
    if ke <= dari:
        return None
    sesi = {
        "tanggal": tanggal or date.today().isoformat(),
        "judul": buku["judul"],
        "dari": dari,
        "ke": ke,
        "dibaca": ke - dari,
    }
    daftar.append(sesi)
    return sesi


def sesi_terakhir(daftar, jumlah=10):
    """Sesi-sesi terbaru (paling baru dulu) + total halaman yang dibaca.

    Kembalikan (daftar_sesi, total_halaman).
    """
    potongan = daftar[-jumlah:] if jumlah > 0 else []
    return list(reversed(potongan)), sum(s["dibaca"] for s in potongan)
