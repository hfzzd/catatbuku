# CatatBuku

Pencatat bacaan berbahasa Indonesia — kelola daftar buku, catat progres
halaman, dan lihat statistik bacaanmu. CLI Python, tanpa dependensi
eksternal, datamu tersimpan lokal di komputermu sendiri.

## Cara jalanin

Tidak perlu instalasi apa-apa (Python 3.9 ke atas, stdlib saja):

```bash
git clone https://github.com/hfzzd/catatbuku
cd catatbuku
python3 -m catatbuku --version   # catatbuku 0.1.0
```

## Contoh

```bash
$ python3 -m catatbuku tambah "Laskar Pelangi" --penulis "Andrea Hirata" --halaman 529
Buku ditambahkan: Laskar Pelangi — Andrea Hirata
Total 529 halaman · status: ingin dibaca

$ python3 -m catatbuku tambah "Bumi Manusia" --penulis "Pramoedya Ananta Toer" --halaman 535
Buku ditambahkan: Bumi Manusia — Pramoedya Ananta Toer
Total 535 halaman · status: ingin dibaca

$ python3 -m catatbuku tambah "Cantik Itu Luka" --penulis "Eka Kurniawan" --halaman 520
Buku ditambahkan: Cantik Itu Luka — Eka Kurniawan
Total 520 halaman · status: ingin dibaca

$ python3 -m catatbuku daftar
1. Laskar Pelangi — Andrea Hirata
   0/529 halaman (0%) · ingin dibaca
2. Bumi Manusia — Pramoedya Ananta Toer
   0/535 halaman (0%) · ingin dibaca
3. Cantik Itu Luka — Eka Kurniawan
   0/520 halaman (0%) · ingin dibaca

$ python3 -m catatbuku progres 1 120
Progres "Laskar Pelangi": 120/529 halaman (23%) · sedang dibaca

$ python3 -m catatbuku progres 2 535
Selamat! Kamu menamatkan "Bumi Manusia" (535 halaman).

$ python3 -m catatbuku daftar --status selesai
2. Bumi Manusia — Pramoedya Ananta Toer
   535/535 halaman (100%) · selesai

$ python3 -m catatbuku daftar --status sedang
1. Laskar Pelangi — Andrea Hirata
   120/529 halaman (23%) · sedang dibaca

$ python3 -m catatbuku statistik
Statistik bacaan
  Total buku: 3
  Ingin dibaca: 1 · Sedang dibaca: 1 · Selesai: 1
  Halaman dibaca: 655/1584 (41%)
  Sedang dibaca:
    1. Laskar Pelangi — 120/529 halaman (23%)

$ python3 -m catatbuku hapus 3
Buku dihapus: Cantik Itu Luka — Eka Kurniawan
Sisa 2 buku di daftar bacaan.

$ python3 -m catatbuku daftar
1. Laskar Pelangi — Andrea Hirata
   120/529 halaman (23%) · sedang dibaca
2. Bumi Manusia — Pramoedya Ananta Toer
   535/535 halaman (100%) · selesai

$ python3 -m catatbuku statistik
Statistik bacaan
  Total buku: 2
  Ingin dibaca: 0 · Sedang dibaca: 1 · Selesai: 1
  Halaman dibaca: 655/1064 (62%)
  Sedang dibaca:
    1. Laskar Pelangi — 120/529 halaman (23%)
```

## Tabel perintah

| Perintah | Fungsi |
| --- | --- |
| `tambah JUDUL --penulis NAMA --halaman N` | Tambah buku baru ke daftar bacaan |
| `daftar [--status ingin\|sedang\|selesai]` | Lihat daftar buku beserta progresnya |
| `progres NOMOR HALAMAN` | Catat sudah sampai halaman berapa (status ikut berubah otomatis) |
| `hapus NOMOR` | Hapus buku dari daftar |
| `statistik` | Ringkasan bacaanmu |
| `--version` | Tampilkan versi CatatBuku |

## Status buku

Status berubah otomatis mengikuti progres halaman:

- **ingin dibaca** — baru ditambahkan, belum mulai dibaca
- **sedang dibaca** — sudah ada progres halaman, belum tamat
- **selesai** — halaman dibaca sudah sama dengan total halaman

## Data tersimpan di mana

Data tersimpan di `~/.config/catatbuku/buku.json` (format JSON, bisa
dibuka dan dibaca langsung). Variabel lingkungan `CATATBUKU_DATA` bisa
dipakai untuk menunjuk berkas lain, berguna saat menjalankan test.

## Rencana

- [x] Day-1: tambah buku, daftar buku, catat progres (status otomatis),
      perintah `hapus` + `statistik`, unit test, README lengkap
- [ ] Day-2: target baca tahunan
- [ ] Day-2: riwayat sesi baca
- [ ] Day-2: ekspor (mis. CSV)

## Menjalankan test

```bash
python3 -m unittest discover -s tests
```

35 test, semua lolos — unit test model (`tests/test_buku.py`) dan
end-to-end CLI (`tests/test_cli.py`, memakai `CATATBUKU_DATA` ke berkas
sementara supaya data asli tidak tersentuh).

## Lisensi

MIT — lihat `LICENSE`.
