"""Unit test ekspor CSV CatatBuku (ekspor.py).

Header, isi baris, judul berkoma dikutip, persen dibulatkan, daftar kosong.
"""

import csv
import os
import tempfile
import unittest

from catatbuku.buku import catat_progres, tambah_buku
from catatbuku.ekspor import HEADER, ekspor_csv


class TestEksporCsv(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "daftar-buku.csv")

    def tearDown(self):
        self.tmp.cleanup()

    def _baca(self):
        with open(self.path, encoding="utf-8", newline="") as f:
            return list(csv.reader(f))

    def test_header_tepat(self):
        ekspor_csv([], self.path)
        baris = self._baca()
        self.assertEqual(len(baris), 1)
        self.assertEqual(
            baris[0],
            [
                "nomor",
                "judul",
                "penulis",
                "halaman_total",
                "halaman_dibaca",
                "persen",
                "status",
                "ditambahkan",
            ],
        )
        self.assertEqual(HEADER, baris[0])

    def test_isi_baris_benar(self):
        daftar = []
        tambah_buku(daftar, "Laskar Pelangi", "Andrea Hirata", 529)
        tambah_buku(daftar, "Bumi Manusia", "Pramoedya", 535)
        catat_progres(daftar, 1, 120)
        jumlah = ekspor_csv(daftar, self.path)
        self.assertEqual(jumlah, 2)
        baris = self._baca()
        self.assertEqual(len(baris), 3)
        self.assertEqual(baris[1][0], "1")
        self.assertEqual(baris[1][1], "Laskar Pelangi")
        self.assertEqual(baris[1][2], "Andrea Hirata")
        self.assertEqual(baris[1][3], "529")
        self.assertEqual(baris[1][4], "120")
        self.assertEqual(baris[1][5], "23")  # round(100*120/529)
        self.assertEqual(baris[1][6], "sedang")
        self.assertEqual(baris[2][0], "2")
        self.assertEqual(baris[2][6], "ingin")
        self.assertEqual(baris[2][5], "0")

    def test_judul_berkoma_dikutip(self):
        daftar = []
        tambah_buku(daftar, "Aku, Kamu, dan Dia", "Penulis", 100)
        ekspor_csv(daftar, self.path)
        with open(self.path, encoding="utf-8") as f:
            mentah = f.read()
        # Judul berkoma harus dikutip agar tetap satu kolom.
        self.assertIn('"Aku, Kamu, dan Dia"', mentah)
        baris = self._baca()
        self.assertEqual(baris[1][1], "Aku, Kamu, dan Dia")
        self.assertEqual(len(baris[1]), 8)

    def test_buku_selesai_persen_seratus(self):
        daftar = []
        tambah_buku(daftar, "A", "Penulis", 100)
        catat_progres(daftar, 1, 100)
        ekspor_csv(daftar, self.path)
        baris = self._baca()
        self.assertEqual(baris[1][5], "100")
        self.assertEqual(baris[1][6], "selesai")

    def test_daftar_kosong_hanya_header(self):
        jumlah = ekspor_csv([], self.path)
        self.assertEqual(jumlah, 0)
        baris = self._baca()
        self.assertEqual(len(baris), 1)

    def test_tanggal_ditambahkan_ikut(self):
        daftar = []
        buku = tambah_buku(daftar, "A", "Penulis", 100)
        ekspor_csv(daftar, self.path)
        baris = self._baca()
        self.assertEqual(baris[1][7], buku["ditambahkan"])


if __name__ == "__main__":
    unittest.main()
