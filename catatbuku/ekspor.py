"""Ekspor daftar buku CatatBuku ke CSV.

Format CSV (satu baris per buku, header di baris pertama):
    nomor,judul,penulis,halaman_total,halaman_dibaca,persen,status,ditambahkan

Kolom status memakai kode (ingin/sedang/selesai) supaya mudah diolah
di spreadsheet; label Bahasa Indonesianya ada di ``buku.label_status``.
"""

import csv

from .buku import persen

HEADER = [
    "nomor",
    "judul",
    "penulis",
    "halaman_total",
    "halaman_dibaca",
    "persen",
    "status",
    "ditambahkan",
]


def ekspor_csv(daftar, path):
    """Tulis daftar buku ke berkas CSV; kembalikan jumlah buku diekspor."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        tulis = csv.writer(f)
        tulis.writerow(HEADER)
        for nomor, buku in enumerate(daftar, start=1):
            tulis.writerow(
                [
                    nomor,
                    buku["judul"],
                    buku["penulis"],
                    buku["halaman_total"],
                    buku["halaman_dibaca"],
                    persen(buku),
                    buku["status"],
                    buku.get("ditambahkan", ""),
                ]
            )
    return len(daftar)
