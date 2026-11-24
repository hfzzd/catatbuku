"""Test end-to-end CLI CatatBuku via subprocess.

Setiap test memakai berkas data sendiri di /tmp lewat env CATATBUKU_DATA,
jadi data asli pengguna tidak tersentuh.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = os.path.join(self.tmp.name, "buku.json")
        self.env = dict(os.environ, CATATBUKU_DATA=self.data)

    def tearDown(self):
        self.tmp.cleanup()

    def jalankan(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "catatbuku", *args],
            cwd=REPO,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def test_tambah_lalu_daftar(self):
        r = self.jalankan(
            "tambah", "Laskar Pelangi", "--penulis", "Andrea Hirata",
            "--halaman", "529",
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Laskar Pelangi", r.stdout)
        r = self.jalankan("daftar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Laskar Pelangi", r.stdout)
        self.assertIn("Andrea Hirata", r.stdout)
        self.assertIn("0/529 halaman (0%)", r.stdout)
        self.assertIn("ingin dibaca", r.stdout)

    def test_daftar_kosong(self):
        r = self.jalankan("daftar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("masih kosong", r.stdout)

    def test_daftar_filter_status(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        self.jalankan("tambah", "B", "--halaman", "200")
        self.jalankan("progres", "2", "200")
        r = self.jalankan("daftar", "--status", "selesai")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("B", r.stdout)
        self.assertNotIn("1. A", r.stdout)
        r = self.jalankan("daftar", "--status", "ingin")
        self.assertIn("A", r.stdout)
        self.assertNotIn("2. B", r.stdout)

    def test_progres_cli(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        r = self.jalankan("progres", "1", "40")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("40/100 halaman (40%)", r.stdout)
        self.assertIn("sedang dibaca", r.stdout)

    def test_progres_selesai_cli(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        r = self.jalankan("progres", "1", "100")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Selamat! Kamu menamatkan", r.stdout)

    def test_hapus_cli(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        self.jalankan("tambah", "B", "--halaman", "200")
        r = self.jalankan("hapus", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Buku dihapus: A", r.stdout)
        self.assertIn("Sisa 1 buku", r.stdout)
        r = self.jalankan("daftar")
        self.assertIn("1. B", r.stdout)
        self.assertNotIn("A", r.stdout)

    def test_statistik_cli(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        self.jalankan("tambah", "B", "--halaman", "200")
        self.jalankan("progres", "2", "100")
        r = self.jalankan("statistik")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Total buku: 2", r.stdout)
        self.assertIn("Ingin dibaca: 1", r.stdout)
        self.assertIn("Sedang dibaca: 1", r.stdout)
        self.assertIn("Selesai: 0", r.stdout)
        self.assertIn("Halaman dibaca: 100/300 (33%)", r.stdout)

    def test_statistik_kosong(self):
        r = self.jalankan("statistik")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("masih kosong", r.stdout)

    def test_error_nomor_tak_ada_exit_1(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        r = self.jalankan("progres", "9", "10")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Tidak ada buku nomor 9", r.stderr)
        r = self.jalankan("hapus", "9")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Tidak ada buku nomor 9", r.stderr)

    def test_error_halaman_lebih_dari_total_exit_1(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        r = self.jalankan("progres", "1", "150")
        self.assertEqual(r.returncode, 1)
        self.assertIn("hanya 100 halaman", r.stderr)

    def test_tambah_halaman_nol_exit_1(self):
        r = self.jalankan("tambah", "A", "--halaman", "0")
        self.assertEqual(r.returncode, 1)
        self.assertIn("lebih dari 0", r.stderr)

    def test_version(self):
        r = self.jalankan("--version")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0.1.0", r.stdout)


if __name__ == "__main__":
    unittest.main()
