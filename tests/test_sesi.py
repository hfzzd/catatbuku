"""Unit test riwayat sesi baca CatatBuku (sesi.py).

Sesi maju/mundur/tanggal selesai, urutan terbaru dulu, simpan-muat.
"""

import json
import os
import tempfile
import unittest
from datetime import date

from catatbuku.buku import CatatBukuError, tambah_buku
from catatbuku.sesi import (
    berkas_sesi,
    catat_sesi,
    muat_sesi,
    sesi_terakhir,
    simpan_sesi,
)


def _buku(judul="Laskar Pelangi"):
    return tambah_buku([], judul, "Andrea Hirata", 529)


class TestCatatSesi(unittest.TestCase):
    def test_catat_maju_ok(self):
        daftar = []
        sesi = catat_sesi(daftar, _buku(), 0, 120)
        self.assertEqual(len(daftar), 1)
        self.assertEqual(sesi["tanggal"], date.today().isoformat())
        self.assertEqual(sesi["judul"], "Laskar Pelangi")
        self.assertEqual(sesi["dari"], 0)
        self.assertEqual(sesi["ke"], 120)
        self.assertEqual(sesi["dibaca"], 120)

    def test_catat_mundur_tidak_dicatat(self):
        daftar = []
        self.assertIsNone(catat_sesi(daftar, _buku(), 200, 100))
        self.assertEqual(daftar, [])

    def test_catat_tetap_tidak_dicatat(self):
        daftar = []
        self.assertIsNone(catat_sesi(daftar, _buku(), 100, 100))
        self.assertEqual(daftar, [])

    def test_catat_tanggal_eksplisit(self):
        daftar = []
        sesi = catat_sesi(daftar, _buku(), 0, 50, tanggal="2026-11-20")
        self.assertEqual(sesi["tanggal"], "2026-11-20")

    def test_catat_judul_tersimpan_bersama_sesi(self):
        daftar = []
        catat_sesi(daftar, _buku("Bumi Manusia"), 0, 30)
        self.assertEqual(daftar[0]["judul"], "Bumi Manusia")

    def test_catat_berurutan_menumpuk(self):
        daftar = []
        catat_sesi(daftar, _buku(), 0, 120)
        catat_sesi(daftar, _buku(), 120, 200)
        self.assertEqual(len(daftar), 2)
        self.assertEqual(daftar[1]["dari"], 120)
        self.assertEqual(daftar[1]["dibaca"], 80)


class TestSesiTerakhir(unittest.TestCase):
    def _tiga_sesi(self):
        daftar = []
        catat_sesi(daftar, _buku("A"), 0, 40, tanggal="2026-11-20")
        catat_sesi(daftar, _buku("B"), 0, 150, tanggal="2026-11-21")
        catat_sesi(daftar, _buku("A"), 40, 80, tanggal="2026-11-22")
        return daftar

    def test_urutan_terbaru_dulu(self):
        terbaru, total = sesi_terakhir(self._tiga_sesi())
        self.assertEqual([s["judul"] for s in terbaru], ["A", "B", "A"])
        self.assertEqual([s["dibaca"] for s in terbaru], [40, 150, 40])

    def test_total_halaman(self):
        _, total = sesi_terakhir(self._tiga_sesi())
        self.assertEqual(total, 230)

    def test_batasi_jumlah(self):
        terbaru, total = sesi_terakhir(self._tiga_sesi(), jumlah=2)
        self.assertEqual(len(terbaru), 2)
        self.assertEqual([s["dibaca"] for s in terbaru], [40, 150])
        self.assertEqual(total, 190)

    def test_jumlah_lebih_besar_dari_isi(self):
        terbaru, total = sesi_terakhir(self._tiga_sesi(), jumlah=10)
        self.assertEqual(len(terbaru), 3)
        self.assertEqual(total, 230)

    def test_jumlah_nol_kosong(self):
        terbaru, total = sesi_terakhir(self._tiga_sesi(), jumlah=0)
        self.assertEqual(terbaru, [])
        self.assertEqual(total, 0)

    def test_daftar_kosong(self):
        terbaru, total = sesi_terakhir([])
        self.assertEqual(terbaru, [])
        self.assertEqual(total, 0)


class TestSimpanMuatSesi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "sesi.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_simpan_muat_round_trip(self):
        daftar = []
        catat_sesi(daftar, _buku(), 0, 120, tanggal="2026-11-20")
        simpan_sesi(daftar, self.path)
        muat = muat_sesi(self.path)
        self.assertEqual(len(muat), 1)
        self.assertEqual(muat[0]["dibaca"], 120)
        self.assertEqual(muat[0]["tanggal"], "2026-11-20")

    def test_muat_berkas_belum_ada_kosong(self):
        self.assertEqual(muat_sesi(self.path), [])

    def test_muat_berkas_rusak_ditolak(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("[{rusak")
        with self.assertRaises(CatatBukuError):
            muat_sesi(self.path)

    def test_muat_bukan_list_ditolak(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"a": 1}, f)
        with self.assertRaises(CatatBukuError):
            muat_sesi(self.path)

    def test_berkas_sesi_di_samping_data(self):
        data = os.path.join(self.tmp.name, "sub", "buku.json")
        self.assertEqual(
            berkas_sesi(data),
            os.path.join(self.tmp.name, "sub", "sesi.json"),
        )


if __name__ == "__main__":
    unittest.main()
