"""Test end-to-end CLI CatatBuku via subprocess.

Setiap test memakai berkas data sendiri di /tmp lewat env CATATBUKU_DATA,
jadi data asli pengguna tidak tersentuh.
"""

import csv
import math
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
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

    # --- target ---

    def test_target_atur_lalu_progres_persen_benar(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        self.jalankan("tambah", "B", "--halaman", "200")
        self.jalankan("progres", "1", "100")
        r = self.jalankan("target", "4")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Target 2026: 4 buku", r.stdout)
        tahun = date.today().year
        bulan_tersisa = 12 - date.today().month + 1
        per_bulan = math.ceil(3 / bulan_tersisa)
        r = self.jalankan("target")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"Target {tahun}: 1/4 buku (25%)", r.stdout)
        self.assertIn(
            f"Sisa 3 buku dalam {bulan_tersisa} bulan — "
            f"butuh sekitar {per_bulan} buku/bulan.",
            r.stdout,
        )

    def test_target_belum_ada_pesan_ramah(self):
        r = self.jalankan("target")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Belum ada target", r.stdout)

    def test_target_nol_exit_1(self):
        r = self.jalankan("target", "0")
        self.assertEqual(r.returncode, 1)
        self.assertIn("lebih dari 0", r.stderr)

    def test_target_tahun_1999_exit_1(self):
        r = self.jalankan("target", "12", "--tahun", "1999")
        self.assertEqual(r.returncode, 1)
        self.assertIn("antara 2000 dan 2100", r.stderr)

    def test_target_tercapai_pesan_selamat(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        self.jalankan("progres", "1", "100")
        self.jalankan("target", "1")
        r = self.jalankan("target")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1/1 buku (100%)", r.stdout)
        self.assertIn("Target tahun ini sudah tercapai", r.stdout)

    # --- sesi ---

    def test_sesi_dua_progres_urutan_terbaru_dulu(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        self.jalankan("tambah", "B", "--halaman", "200")
        self.jalankan("progres", "1", "40")
        self.jalankan("progres", "2", "150")
        self.jalankan("progres", "1", "80")
        r = self.jalankan("sesi")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Riwayat sesi baca (3 terakhir)", r.stdout)
        self.assertIn("Total: 230 halaman dalam 3 sesi.", r.stdout)
        # Terbaru dulu: A 40→80, lalu B 0→150, lalu A 0→40.
        i1 = r.stdout.index("A: 40 → 80")
        i2 = r.stdout.index("B: 0 → 150")
        i3 = r.stdout.index("A: 0 → 40")
        self.assertLess(i1, i2)
        self.assertLess(i2, i3)

    def test_sesi_progres_mundur_tidak_tercatat(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        self.jalankan("progres", "1", "40")
        self.jalankan("progres", "1", "20")
        r = self.jalankan("sesi")
        self.assertIn("Total: 40 halaman dalam 1 sesi.", r.stdout)

    def test_sesi_kosong_exit_0(self):
        r = self.jalankan("sesi")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Belum ada sesi baca", r.stdout)

    def test_sesi_jumlah_satu(self):
        self.jalankan("tambah", "A", "--halaman", "100")
        self.jalankan("progres", "1", "40")
        self.jalankan("progres", "1", "80")
        r = self.jalankan("sesi", "--jumlah", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Riwayat sesi baca (1 terakhir)", r.stdout)
        self.assertIn("A: 40 → 80", r.stdout)
        self.assertNotIn("A: 0 → 40", r.stdout)
        self.assertIn("Total: 40 halaman dalam 1 sesi.", r.stdout)

    # --- ekspor ---

    def test_ekspor_csv_isi_benar(self):
        self.jalankan(
            "tambah", "Laskar, Pelangi", "--penulis", "Andrea Hirata",
            "--halaman", "529",
        )
        self.jalankan("tambah", "B", "--halaman", "200")
        self.jalankan("progres", "1", "120")
        berkas = os.path.join(self.tmp.name, "buku.csv")
        r = self.jalankan("ekspor", berkas)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Diekspor 2 buku", r.stdout)
        with open(berkas, encoding="utf-8", newline="") as f:
            baris = list(csv.reader(f))
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
        self.assertEqual(baris[1][1], "Laskar, Pelangi")
        self.assertEqual(baris[1][4], "120")
        self.assertEqual(baris[1][5], "23")
        self.assertEqual(baris[1][6], "sedang")
        self.assertEqual(baris[2][1], "B")
        self.assertEqual(baris[2][6], "ingin")

    def test_ekspor_kosong_exit_0(self):
        berkas = os.path.join(self.tmp.name, "buku.csv")
        r = self.jalankan("ekspor", berkas)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("masih kosong", r.stdout)
        self.assertFalse(os.path.exists(berkas))


if __name__ == "__main__":
    unittest.main()
