"""Antarmuka baris perintah CatatBuku."""

import argparse
import sys

from . import __version__
from .buku import (
    STATUS_INGIN,
    STATUS_LABEL,
    STATUS_SEDANG,
    STATUS_SELESAI,
    CatatBukuError,
    catat_progres,
    hapus_buku,
    label_status,
    muat,
    persen,
    simpan,
    statistik,
    tambah_buku,
)


def _parser():
    p = argparse.ArgumentParser(
        prog="catatbuku",
        description="CatatBuku — pencatat bacaan berbahasa Indonesia.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="perintah")

    t = sub.add_parser("tambah", help="Tambah buku baru ke daftar bacaan.")
    t.add_argument("judul", help="Judul buku.")
    t.add_argument("--penulis", default="-", help="Nama penulis.")
    t.add_argument(
        "--halaman", type=int, required=True, help="Jumlah total halaman buku."
    )

    d = sub.add_parser("daftar", help="Lihat daftar buku beserta progresnya.")
    d.add_argument(
        "--status",
        choices=[STATUS_INGIN, STATUS_SEDANG, STATUS_SELESAI],
        help="Tampilkan hanya buku dengan status ini.",
    )

    pr = sub.add_parser(
        "progres", help="Catat sudah sampai halaman berapa."
    )
    pr.add_argument("nomor", type=int, help="Nomor buku (lihat `daftar`).")
    pr.add_argument("halaman", type=int, help="Halaman terakhir yang dibaca.")

    h = sub.add_parser("hapus", help="Hapus buku dari daftar bacaan.")
    h.add_argument("nomor", type=int, help="Nomor buku (lihat `daftar`).")

    sub.add_parser("statistik", help="Lihat ringkasan statistik bacaan.")

    return p


def _format_buku(nomor, buku):
    baris = (
        f"{nomor}. {buku['judul']} — {buku['penulis']}\n"
        f"   {buku['halaman_dibaca']}/{buku['halaman_total']} halaman "
        f"({persen(buku)}%) · {label_status(buku['status'])}"
    )
    return baris


def _cmd_tambah(args):
    daftar = muat()
    buku = tambah_buku(daftar, args.judul, args.penulis, args.halaman)
    simpan(daftar)
    print(f"Buku ditambahkan: {buku['judul']} — {buku['penulis']}")
    print(f"Total {buku['halaman_total']} halaman · status: ingin dibaca")
    return 0


def _cmd_daftar(args):
    daftar = muat()
    if args.status:
        daftar = [b for b in daftar if b["status"] == args.status]
    if not daftar:
        if args.status:
            print(
                f"Belum ada buku dengan status "
                f"'{STATUS_LABEL[args.status]}'."
            )
        else:
            print(
                "Daftar bacaan masih kosong. Tambah buku dulu:\n"
                '  catatbuku tambah "Judul Buku" --penulis "Nama" --halaman 200'
            )
        return 0
    # Nomor urut mengikuti urutan daftar penuh, bukan hasil saring.
    for nomor, buku in enumerate(muat(), start=1):
        if args.status and buku["status"] != args.status:
            continue
        print(_format_buku(nomor, buku))
    return 0


def _cmd_hapus(args):
    daftar = muat()
    buku = hapus_buku(daftar, args.nomor)
    simpan(daftar)
    print(f"Buku dihapus: {buku['judul']} — {buku['penulis']}")
    print(f"Sisa {len(daftar)} buku di daftar bacaan.")
    return 0


def _cmd_statistik(args):
    daftar = muat()
    if not daftar:
        print(
            "Daftar bacaan masih kosong, jadi belum ada statistik. "
            "Tambah buku dulu:\n"
            '  catatbuku tambah "Judul Buku" --penulis "Nama" --halaman 200'
        )
        return 0
    stat = statistik(daftar)
    per = stat["per_status"]
    print("Statistik bacaan")
    print(f"  Total buku: {stat['total']}")
    print(
        f"  Ingin dibaca: {per[STATUS_INGIN]} · "
        f"Sedang dibaca: {per[STATUS_SEDANG]} · "
        f"Selesai: {per[STATUS_SELESAI]}"
    )
    print(
        f"  Halaman dibaca: {stat['total_dibaca']}/"
        f"{stat['total_halaman']} ({stat['persen']}%)"
    )
    if stat["sedang"]:
        print("  Sedang dibaca:")
        for nomor, buku in stat["sedang"]:
            print(
                f"    {nomor}. {buku['judul']} — "
                f"{buku['halaman_dibaca']}/{buku['halaman_total']} halaman "
                f"({persen(buku)}%)"
            )
    return 0


def _cmd_progres(args):
    daftar = muat()
    buku = catat_progres(daftar, args.nomor, args.halaman)
    simpan(daftar)
    if buku["status"] == STATUS_SELESAI:
        print(
            f"Selamat! Kamu menamatkan \"{buku['judul']}\" "
            f"({buku['halaman_total']} halaman)."
        )
    else:
        print(
            f"Progres \"{buku['judul']}\": "
            f"{buku['halaman_dibaca']}/{buku['halaman_total']} halaman "
            f"({persen(buku)}%) · {label_status(buku['status'])}"
        )
    return 0


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        if args.perintah == "tambah":
            return _cmd_tambah(args)
        if args.perintah == "daftar":
            return _cmd_daftar(args)
        if args.perintah == "hapus":
            return _cmd_hapus(args)
        if args.perintah == "statistik":
            return _cmd_statistik(args)
        if args.perintah == "progres":
            return _cmd_progres(args)
        _parser().print_help()
        return 0
    except CatatBukuError as exc:
        print(f"Maaf, {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
