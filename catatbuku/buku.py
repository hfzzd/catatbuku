"""Model dan penyimpanan daftar buku CatatBuku.

Satu buku adalah dict:
    {
        "judul": str,
        "penulis": str,
        "halaman_total": int,
        "halaman_dibaca": int,
        "status": "ingin" | "sedang" | "selesai",
        "ditambahkan": "YYYY-MM-DD",
    }

Status dihitung dari progres halaman:
- 0 halaman dibaca -> "ingin" (ingin dibaca)
- sebagian -> "sedang" (sedang dibaca)
- halaman dibaca == total -> "selesai"
"""

import json
import os
from datetime import date

STATUS_INGIN = "ingin"
STATUS_SEDANG = "sedang"
STATUS_SELESAI = "selesai"

STATUS_LABEL = {
    STATUS_INGIN: "ingin dibaca",
    STATUS_SEDANG: "sedang dibaca",
    STATUS_SELESAI: "selesai",
}


class CatatBukuError(Exception):
    """Kesalahan ramah-pengguna (input salah, berkas rusak, dsb)."""


def berkas_data():
    """Lokasi berkas JSON daftar buku.

    Variabel lingkungan CATATBUKU_DATA menunjuk berkas lain — dipakai
    saat menjalankan test supaya data asli tidak tersentuh.
    """
    env = os.environ.get("CATATBUKU_DATA")
    if env:
        return env
    return os.path.join(
        os.path.expanduser("~"), ".config", "catatbuku", "buku.json"
    )


def muat(path=None):
    """Muat daftar buku dari berkas JSON; [] bila berkas belum ada."""
    path = path or berkas_data()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError) as exc:
        raise CatatBukuError(
            f"Berkas data {path} tidak bisa dibaca ({exc}). "
            "Periksa berkasnya atau hapus lalu mulai lagi."
        ) from exc
    if not isinstance(data, list):
        raise CatatBukuError(
            f"Berkas data {path} formatnya salah (harusnya berisi daftar buku)."
        )
    return data


def simpan(daftar, path=None):
    """Simpan daftar buku ke berkas JSON (buat direktorinya bila perlu)."""
    path = path or berkas_data()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(daftar, f, ensure_ascii=False, indent=2)
        f.write("\n")


def tambah_buku(daftar, judul, penulis, halaman_total):
    """Tambah satu buku baru (status awal: ingin dibaca)."""
    judul = (judul or "").strip()
    if not judul:
        raise CatatBukuError("Judul buku tidak boleh kosong.")
    penulis = (penulis or "-").strip() or "-"
    if not isinstance(halaman_total, int) or isinstance(halaman_total, bool):
        raise CatatBukuError("Jumlah halaman harus bilangan bulat.")
    if halaman_total <= 0:
        raise CatatBukuError("Jumlah halaman harus lebih dari 0.")
    buku = {
        "judul": judul,
        "penulis": penulis,
        "halaman_total": halaman_total,
        "halaman_dibaca": 0,
        "status": STATUS_INGIN,
        "ditambahkan": date.today().isoformat(),
    }
    daftar.append(buku)
    return buku


def ambil(daftar, nomor):
    """Ambil buku berdasarkan nomor urut (mulai 1), sesuai urutan daftar."""
    if not isinstance(nomor, int) or isinstance(nomor, bool):
        raise CatatBukuError("Nomor buku harus bilangan bulat.")
    if nomor < 1 or nomor > len(daftar):
        raise CatatBukuError(
            f"Tidak ada buku nomor {nomor}. "
            f"Daftar saat ini berisi {len(daftar)} buku."
        )
    return daftar[nomor - 1]


def persen(buku):
    """Persen progres baca, dibulatkan (0–100)."""
    total = buku["halaman_total"]
    if total <= 0:
        return 0
    return round(100 * buku["halaman_dibaca"] / total)


def catat_progres(daftar, nomor, halaman):
    """Catat sudah sampai halaman berapa; status ikut berubah otomatis."""
    buku = ambil(daftar, nomor)
    if not isinstance(halaman, int) or isinstance(halaman, bool):
        raise CatatBukuError("Halaman harus bilangan bulat.")
    if halaman < 0:
        raise CatatBukuError("Halaman tidak boleh negatif.")
    if halaman > buku["halaman_total"]:
        raise CatatBukuError(
            f"Buku ini hanya {buku['halaman_total']} halaman, "
            f"jadi halaman {halaman} tidak ada."
        )
    buku["halaman_dibaca"] = halaman
    if halaman == 0:
        buku["status"] = STATUS_INGIN
    elif halaman == buku["halaman_total"]:
        buku["status"] = STATUS_SELESAI
    else:
        buku["status"] = STATUS_SEDANG
    return buku


def hapus_buku(daftar, nomor):
    """Hapus buku berdasarkan nomor urut; kembalikan buku yang dihapus."""
    buku = ambil(daftar, nomor)
    del daftar[nomor - 1]
    return buku


def label_status(status):
    """Label Bahasa Indonesia untuk sebuah kode status."""
    return STATUS_LABEL.get(status, status)
