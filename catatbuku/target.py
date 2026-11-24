"""Target baca tahunan CatatBuku.

Target disimpan per tahun di berkas ``target.json`` (di samping berkas
data buku, jadi ikut terisolasi oleh env CATATBUKU_DATA saat test).
Satu entri: {"2026": 12} artinya target menamatkan 12 buku di tahun 2026.

Buku yang dihitung selesai di suatu tahun adalah buku berstatus selesai
yang tanggal selesainya (``buku["selesai"]``, dicatat otomatis oleh
``catat_progres`` saat status berubah jadi selesai) jatuh di tahun itu.
Buku selesai tanpa tanggal (data lama dari Day-1) ikut dihitung di tahun
berjalan, supaya target tetap masuk akal untuk data yang sudah ada.
"""

import json
import math
import os
from datetime import date

from .buku import STATUS_SELESAI, CatatBukuError, berkas_data


def berkas_target(path_buku=None):
    """Lokasi berkas target (target.json di samping berkas data buku)."""
    buku = path_buku or berkas_data()
    return os.path.join(os.path.dirname(buku), "target.json")


def muat_target(path=None):
    """Muat target per tahun; {} bila berkas belum ada."""
    path = path or berkas_target()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError) as exc:
        raise CatatBukuError(
            f"Berkas target {path} tidak bisa dibaca ({exc}). "
            "Periksa berkasnya atau hapus lalu mulai lagi."
        ) from exc
    if not isinstance(data, dict):
        raise CatatBukuError(
            f"Berkas target {path} formatnya salah "
            "(harusnya berisi target per tahun)."
        )
    return data


def simpan_target(targets, path=None):
    """Simpan target per tahun ke berkas JSON."""
    path = path or berkas_target()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(targets, f, ensure_ascii=False, indent=2)
        f.write("\n")


def atur_target(targets, tahun, jumlah):
    """Atur target jumlah buku untuk satu tahun."""
    if not isinstance(tahun, int) or isinstance(tahun, bool):
        raise CatatBukuError("Tahun harus bilangan bulat.")
    if tahun < 2000 or tahun > 2100:
        raise CatatBukuError("Tahun harus antara 2000 dan 2100.")
    if not isinstance(jumlah, int) or isinstance(jumlah, bool):
        raise CatatBukuError("Target harus bilangan bulat.")
    if jumlah <= 0:
        raise CatatBukuError("Target harus lebih dari 0 buku.")
    targets[str(tahun)] = jumlah
    return jumlah


def hitung_target(daftar, targets, tahun=None):
    """Hitung progres target tahunan.

    Kembalikan dict: tahun, target, selesai, persen, sisa,
    bulan_tersisa, per_bulan (buku/bulan yang masih dibutuhkan,
    dibulatkan ke atas; None bila tahun sudah lewat).
    """
    tahun = tahun if tahun is not None else date.today().year
    target = targets.get(str(tahun))
    selesai = 0
    for buku in daftar:
        if buku["status"] != STATUS_SELESAI:
            continue
        tgl_selesai = buku.get("selesai")
        if tgl_selesai is None:
            # Data lama tanpa tanggal selesai: hitung di tahun berjalan.
            if tahun == date.today().year:
                selesai += 1
        elif tgl_selesai[:4] == str(tahun):
            selesai += 1
    hari_ini = date.today()
    if tahun < hari_ini.year:
        bulan_tersisa = 0
    elif tahun > hari_ini.year:
        bulan_tersisa = 12
    else:
        bulan_tersisa = 12 - hari_ini.month + 1
    if target is None:
        return {
            "tahun": tahun,
            "target": None,
            "selesai": selesai,
            "persen": 0,
            "sisa": 0,
            "bulan_tersisa": bulan_tersisa,
            "per_bulan": None,
        }
    sisa = max(0, target - selesai)
    persen = round(100 * selesai / target) if target else 0
    per_bulan = (
        math.ceil(sisa / bulan_tersisa) if bulan_tersisa > 0 else None
    )
    return {
        "tahun": tahun,
        "target": target,
        "selesai": selesai,
        "persen": persen,
        "sisa": sisa,
        "bulan_tersisa": bulan_tersisa,
        "per_bulan": per_bulan,
    }
