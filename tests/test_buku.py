"""Unit test model CatatBuku (buku.py): tambah, ambil, progres, simpan-muat."""

import json
import os
import tempfile
import unittest

from catatbuku.buku import (
    CatatBukuError,
    ambil,
    berkas_data,
    catat_progres,
    hapus_buku,
    label_status,
    muat,
    persen,
    simpan,
    statistik,
    tambah_buku,
)


class TestTambahBuku(unittest.TestCase):
    def test_tambah_ok(self):
        daftar = []
        buku = tambah_buku(daftar, "Laskar Pelangi", "Andrea Hirata", 529)
        self.assertEqual(len(daftar), 1)
        self.assertEqual(buku["judul"], "Laskar Pelangi")
        self.assertEqual(buku["penulis"], "Andrea Hirata")
        self.assertEqual(buku["halaman_total"], 529)
        self.assertEqual(buku["halaman_dibaca"], 0)
        self.assertEqual(buku["status"], "ingin")

    def test_tambah_judul_kosong_ditolak(self):
        with self.assertRaises(CatatBukuError):
            tambah_buku([], "", "Penulis", 100)

    def test_tambah_judul_spasi_saja_ditolak(self):
        with self.assertRaises(CatatBukuError):
            tambah_buku([], "   ", "Penulis", 100)

    def test_tambah_halaman_nol_ditolak(self):
        with self.assertRaises(CatatBukuError):
            tambah_buku([], "Judul", "Penulis", 0)

    def test_tambah_halaman_negatif_ditolak(self):
        with self.assertRaises(CatatBukuError):
            tambah_buku([], "Judul", "Penulis", -50)

    def test_tambah_penulis_kosong_jadi_strip(self):
        buku = tambah_buku([], "Judul", "", 100)
        self.assertEqual(buku["penulis"], "-")

    def test_tambah_penulis_spasi_jadi_strip(self):
        buku = tambah_buku([], "Judul", "   ", 100)
        self.assertEqual(buku["penulis"], "-")


class TestAmbilBuku(unittest.TestCase):
    def setUp(self):
        self.daftar = []
        tambah_buku(self.daftar, "Buku Satu", "A", 100)
        tambah_buku(self.daftar, "Buku Dua", "B", 200)

    def test_ambil_ok(self):
        self.assertEqual(ambil(self.daftar, 2)["judul"], "Buku Dua")

    def test_ambil_nomor_tak_ada_ditolak(self):
        with self.assertRaises(CatatBukuError):
            ambil(self.daftar, 9)

    def test_ambil_nomor_nol_ditolak(self):
        with self.assertRaises(CatatBukuError):
            ambil(self.daftar, 0)


class TestProgres(unittest.TestCase):
    def setUp(self):
        self.daftar = []
        tambah_buku(self.daftar, "Buku", "A", 200)

    def test_progres_status_otomatis(self):
        # 0 halaman -> ingin dibaca
        buku = catat_progres(self.daftar, 1, 0)
        self.assertEqual(buku["status"], "ingin")
        # sebagian -> sedang dibaca
        buku = catat_progres(self.daftar, 1, 50)
        self.assertEqual(buku["status"], "sedang")
        self.assertEqual(buku["halaman_dibaca"], 50)
        # penuh -> selesai
        buku = catat_progres(self.daftar, 1, 200)
        self.assertEqual(buku["status"], "selesai")
        # kembali ke 0 -> ingin dibaca lagi
        buku = catat_progres(self.daftar, 1, 0)
        self.assertEqual(buku["status"], "ingin")

    def test_progres_halaman_lebih_dari_total_ditolak(self):
        with self.assertRaises(CatatBukuError):
            catat_progres(self.daftar, 1, 201)

    def test_progres_halaman_negatif_ditolak(self):
        with self.assertRaises(CatatBukuError):
            catat_progres(self.daftar, 1, -1)

    def test_persen_dibulatkan(self):
        buku = {"halaman_dibaca": 1, "halaman_total": 3}
        self.assertEqual(persen(buku), 33)
        buku = {"halaman_dibaca": 2, "halaman_total": 3}
        self.assertEqual(persen(buku), 67)
        buku = {"halaman_dibaca": 0, "halaman_total": 3}
        self.assertEqual(persen(buku), 0)
        buku = {"halaman_dibaca": 3, "halaman_total": 3}
        self.assertEqual(persen(buku), 100)


class TestSimpanMuat(unittest.TestCase):
    def test_simpan_muat_round_trip(self):
        daftar = []
        tambah_buku(daftar, "Laskar Pelangi", "Andrea Hirata", 529)
        tambah_buku(daftar, "Bumi Manusia", "Pramoedya", 535)
        catat_progres(daftar, 2, 120)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "buku.json")
            simpan(daftar, path)
            hasil = muat(path)
        self.assertEqual(len(hasil), 2)
        self.assertEqual(hasil[0]["judul"], "Laskar Pelangi")
        self.assertEqual(hasil[1]["halaman_dibaca"], 120)
        self.assertEqual(hasil[1]["status"], "sedang")

    def test_muat_berkas_belum_ada_kosong(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "belum-ada.json")
            self.assertEqual(muat(path), [])

    def test_berkas_rusak_ditolak_ramah(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "rusak.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{ini bukan json")
            with self.assertRaises(CatatBukuError):
                muat(path)

    def test_berkas_bukan_daftar_ditolak(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "salah.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"judul": "bukan daftar"}, f)
            with self.assertRaises(CatatBukuError):
                muat(path)

    def test_env_catatbuku_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "khusus.json")
            lama = os.environ.get("CATATBUKU_DATA")
            os.environ["CATATBUKU_DATA"] = path
            try:
                self.assertEqual(berkas_data(), path)
            finally:
                if lama is None:
                    del os.environ["CATATBUKU_DATA"]
                else:
                    os.environ["CATATBUKU_DATA"] = lama


class TestStatistikDanLainnya(unittest.TestCase):
    def test_statistik_hitung_benar(self):
        daftar = []
        tambah_buku(daftar, "A", "X", 100)
        tambah_buku(daftar, "B", "Y", 200)
        tambah_buku(daftar, "C", "Z", 300)
        catat_progres(daftar, 2, 100)
        catat_progres(daftar, 3, 300)
        stat = statistik(daftar)
        self.assertEqual(stat["total"], 3)
        self.assertEqual(stat["per_status"]["ingin"], 1)
        self.assertEqual(stat["per_status"]["sedang"], 1)
        self.assertEqual(stat["per_status"]["selesai"], 1)
        self.assertEqual(stat["total_dibaca"], 400)
        self.assertEqual(stat["total_halaman"], 600)
        self.assertEqual(stat["persen"], 67)
        self.assertEqual(len(stat["sedang"]), 1)
        self.assertEqual(stat["sedang"][0][0], 2)

    def test_statistik_kosong(self):
        stat = statistik([])
        self.assertEqual(stat["total"], 0)
        self.assertEqual(stat["total_dibaca"], 0)
        self.assertEqual(stat["persen"], 0)

    def test_hapus_buku(self):
        daftar = []
        tambah_buku(daftar, "A", "X", 100)
        tambah_buku(daftar, "B", "Y", 200)
        hapus = hapus_buku(daftar, 1)
        self.assertEqual(hapus["judul"], "A")
        self.assertEqual(len(daftar), 1)
        self.assertEqual(daftar[0]["judul"], "B")
        with self.assertRaises(CatatBukuError):
            hapus_buku(daftar, 5)

    def test_label_status(self):
        self.assertEqual(label_status("ingin"), "ingin dibaca")
        self.assertEqual(label_status("sedang"), "sedang dibaca")
        self.assertEqual(label_status("selesai"), "selesai")


if __name__ == "__main__":
    unittest.main()
