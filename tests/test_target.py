"""Unit test target baca tahunan CatatBuku (target.py).

Atur/validasi target, hitung progres + per_bulan, simpan-muat berkas.
Bulan tersisa dihitung dari tanggal hari ini, jadi ekspektasi yang
bergantung bulan dihitung dinamis dari date.today().
"""

import json
import math
import os
import tempfile
import unittest
from datetime import date

from catatbuku.buku import CatatBukuError, tambah_buku, catat_progres
from catatbuku.target import (
    atur_target,
    berkas_target,
    hitung_target,
    muat_target,
    simpan_target,
)

TAHUN_INI = date.today().year


def _buku_selesai(judul, total, tanggal_selesai):
    """Buku selesai dengan tanggal selesai tertentu (bisa None = data lama)."""
    buku = tambah_buku([], judul, "Penulis", total)
    buku["halaman_dibaca"] = total
    buku["status"] = "selesai"
    if tanggal_selesai is None:
        buku.pop("selesai", None)
    else:
        buku["selesai"] = tanggal_selesai
    return buku


class TestAturTarget(unittest.TestCase):
    def test_atur_ok(self):
        targets = {}
        hasil = atur_target(targets, 2026, 12)
        self.assertEqual(hasil, 12)
        self.assertEqual(targets, {"2026": 12})

    def test_atur_timpa_tahun_yang_sama(self):
        targets = {"2026": 12}
        atur_target(targets, 2026, 20)
        self.assertEqual(targets, {"2026": 20})

    def test_atur_jumlah_nol_ditolak(self):
        with self.assertRaises(CatatBukuError):
            atur_target({}, 2026, 0)

    def test_atur_jumlah_negatif_ditolak(self):
        with self.assertRaises(CatatBukuError):
            atur_target({}, 2026, -5)

    def test_atur_jumlah_bukan_int_ditolak(self):
        with self.assertRaises(CatatBukuError):
            atur_target({}, 2026, 12.5)
        with self.assertRaises(CatatBukuError):
            atur_target({}, 2026, "12")

    def test_atur_jumlah_bool_ditolak(self):
        with self.assertRaises(CatatBukuError):
            atur_target({}, 2026, True)

    def test_atur_tahun_terlalu_lama_ditolak(self):
        with self.assertRaises(CatatBukuError):
            atur_target({}, 1999, 12)

    def test_atur_tahun_terlalu_jauh_ditolak(self):
        with self.assertRaises(CatatBukuError):
            atur_target({}, 2101, 12)

    def test_atur_tahun_batas_bawah_ok(self):
        atur_target({}, 2000, 1)

    def test_atur_tahun_batas_atas_ok(self):
        atur_target({}, 2100, 1)

    def test_atur_tahun_bukan_int_ditolak(self):
        with self.assertRaises(CatatBukuError):
            atur_target({}, "2026", 12)


class TestHitungTarget(unittest.TestCase):
    def test_belum_ada_target(self):
        hasil = hitung_target([], {}, TAHUN_INI)
        self.assertEqual(hasil["tahun"], TAHUN_INI)
        self.assertIsNone(hasil["target"])
        self.assertEqual(hasil["selesai"], 0)
        self.assertEqual(hasil["persen"], 0)
        self.assertEqual(hasil["sisa"], 0)
        self.assertIsNone(hasil["per_bulan"])

    def test_progres_dan_persen(self):
        daftar = [
            _buku_selesai("A", 100, f"{TAHUN_INI}-03-10"),
            _buku_selesai("B", 200, f"{TAHUN_INI}-07-22"),
        ]
        hasil = hitung_target(daftar, {str(TAHUN_INI): 12}, TAHUN_INI)
        self.assertEqual(hasil["selesai"], 2)
        self.assertEqual(hasil["persen"], 17)  # round(100*2/12)
        self.assertEqual(hasil["sisa"], 10)

    def test_per_bulan_dibulatkan_ke_atas(self):
        bulan_tersisa = 12 - date.today().month + 1
        daftar = [_buku_selesai("A", 100, f"{TAHUN_INI}-01-05")]
        hasil = hitung_target(daftar, {str(TAHUN_INI): 12}, TAHUN_INI)
        self.assertEqual(hasil["bulan_tersisa"], bulan_tersisa)
        self.assertEqual(hasil["sisa"], 11)
        self.assertEqual(hasil["per_bulan"], math.ceil(11 / bulan_tersisa))

    def test_target_tercapai(self):
        daftar = [
            _buku_selesai("A", 100, f"{TAHUN_INI}-01-05"),
            _buku_selesai("B", 200, f"{TAHUN_INI}-02-05"),
        ]
        hasil = hitung_target(daftar, {str(TAHUN_INI): 2}, TAHUN_INI)
        self.assertEqual(hasil["selesai"], 2)
        self.assertEqual(hasil["persen"], 100)
        self.assertEqual(hasil["sisa"], 0)
        self.assertEqual(hasil["per_bulan"], 0)

    def test_buku_selesai_tahun_lain_tidak_dihitung(self):
        daftar = [_buku_selesai("A", 100, f"{TAHUN_INI - 1}-12-20")]
        hasil = hitung_target(daftar, {str(TAHUN_INI): 12}, TAHUN_INI)
        self.assertEqual(hasil["selesai"], 0)
        hasil_lalu = hitung_target(daftar, {str(TAHUN_INI - 1): 12}, TAHUN_INI - 1)
        self.assertEqual(hasil_lalu["selesai"], 1)

    def test_buku_selesai_tanpa_tanggal_dihitung_tahun_berjalan(self):
        daftar = [_buku_selesai("A", 100, None)]
        hasil = hitung_target(daftar, {str(TAHUN_INI): 12}, TAHUN_INI)
        self.assertEqual(hasil["selesai"], 1)
        hasil_lain = hitung_target(daftar, {str(TAHUN_INI + 1): 12}, TAHUN_INI + 1)
        self.assertEqual(hasil_lain["selesai"], 0)

    def test_buku_belum_selesai_tidak_dihitung(self):
        daftar = [tambah_buku([], "A", "Penulis", 100)]
        catat_progres(daftar, 1, 40)
        hasil = hitung_target(daftar, {str(TAHUN_INI): 12}, TAHUN_INI)
        self.assertEqual(hasil["selesai"], 0)

    def test_tahun_lalu_bulan_tersisa_nol(self):
        hasil = hitung_target([], {str(TAHUN_INI - 1): 12}, TAHUN_INI - 1)
        self.assertEqual(hasil["bulan_tersisa"], 0)
        self.assertIsNone(hasil["per_bulan"])

    def test_tahun_depan_bulan_tersisa_dua_belas(self):
        hasil = hitung_target([], {str(TAHUN_INI + 1): 12}, TAHUN_INI + 1)
        self.assertEqual(hasil["bulan_tersisa"], 12)
        self.assertEqual(hasil["per_bulan"], 1)


class TestSimpanMuatTarget(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "target.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_simpan_muat_round_trip(self):
        simpan_target({"2026": 12, "2027": 20}, self.path)
        self.assertEqual(muat_target(self.path), {"2026": 12, "2027": 20})

    def test_muat_berkas_belum_ada_kosong(self):
        self.assertEqual(muat_target(self.path), {})

    def test_muat_berkas_rusak_ditolak(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{bukan json")
        with self.assertRaises(CatatBukuError):
            muat_target(self.path)

    def test_muat_bukan_dict_ditolak(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([1, 2], f)
        with self.assertRaises(CatatBukuError):
            muat_target(self.path)

    def test_berkas_target_di_samping_data(self):
        data = os.path.join(self.tmp.name, "sub", "buku.json")
        self.assertEqual(
            berkas_target(data),
            os.path.join(self.tmp.name, "sub", "target.json"),
        )

    def test_berkas_target_ikut_env_catatbuku_data(self):
        data = os.path.join(self.tmp.name, "buku.json")
        lama = os.environ.get("CATATBUKU_DATA")
        os.environ["CATATBUKU_DATA"] = data
        try:
            self.assertEqual(
                berkas_target(),
                os.path.join(self.tmp.name, "target.json"),
            )
        finally:
            if lama is None:
                del os.environ["CATATBUKU_DATA"]
            else:
                os.environ["CATATBUKU_DATA"] = lama


if __name__ == "__main__":
    unittest.main()
