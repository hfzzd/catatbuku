# CatatBuku

Pencatat bacaan berbahasa Indonesia — kelola daftar buku, catat progres
halaman, lihat statistik bacaan, pasang target tahunan, dan ekspor daftar
bukumu. CLI Python, tanpa dependensi eksternal, datamu tersimpan lokal di
komputermu sendiri.

## Cara jalanin

Tidak perlu instalasi apa-apa (Python 3.9 ke atas, stdlib saja):

```bash
git clone https://github.com/hfzzd/catatbuku
cd catatbuku
python3 -m catatbuku --version   # catatbuku 0.2.0
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

### Target baca tahunan

```bash
$ python3 -m catatbuku target 12
Target 2026: 12 buku. Semangat membacanya!

$ python3 -m catatbuku target
Target 2026: 1/12 buku (8%)
Sisa 11 buku dalam 2 bulan — butuh sekitar 6 buku/bulan.
```

Target dihitung dari buku yang berstatus selesai di tahun itu. Perintah
`target` tanpa angka menampilkan progresnya, lengkap dengan perkiraan
buku per bulan yang masih dibutuhkan sampai akhir tahun. Tahun lain bisa
diatur dengan `--tahun`, contoh: `catatbuku target 24 --tahun 2027`.

### Riwayat sesi baca

Setiap kali progres sebuah buku maju lewat `progres`, satu sesi tercatat
otomatis (tanggal, judul, halaman sebelum dan sesudahnya):

```bash
$ python3 -m catatbuku sesi
Riwayat sesi baca (2 terakhir)
  2026-11-25 — Bumi Manusia: 0 → 535 (535 halaman)
  2026-11-25 — Laskar Pelangi: 0 → 120 (120 halaman)
Total: 655 halaman dalam 2 sesi.

$ python3 -m catatbuku sesi --jumlah 1
Riwayat sesi baca (1 terakhir)
  2026-11-25 — Bumi Manusia: 0 → 535 (535 halaman)
Total: 535 halaman dalam 1 sesi.
```

Sesi ditampilkan dari yang paling baru. Memundurkan halaman (misalnya
ralat) tidak tercatat sebagai sesi.

### Ekspor ke CSV

```bash
$ python3 -m catatbuku ekspor
Diekspor 2 buku ke daftar-buku.csv.

$ cat daftar-buku.csv
nomor,judul,penulis,halaman_total,halaman_dibaca,persen,status,ditambahkan
1,Laskar Pelangi,Andrea Hirata,529,120,23,sedang,2026-11-25
2,Bumi Manusia,Pramoedya Ananta Toer,535,535,100,selesai,2026-11-25

$ python3 -m catatbuku ekspor buku-2026.csv
Diekspor 2 buku ke buku-2026.csv.
```

Nama berkas tujuan boleh diisi sendiri; tanpa nama, berkasnya
`daftar-buku.csv` di folder tempat perintah dijalankan. Kolom `status`
memakai kode (`ingin`/`sedang`/`selesai`) supaya mudah diolah di
spreadsheet.

## Tabel perintah

| Perintah | Fungsi |
| --- | --- |
| `tambah JUDUL --penulis NAMA --halaman N` | Tambah buku baru ke daftar bacaan |
| `daftar [--status ingin\|sedang\|selesai]` | Lihat daftar buku beserta progresnya |
| `progres NOMOR HALAMAN` | Catat sudah sampai halaman berapa (status ikut berubah otomatis) |
| `hapus NOMOR` | Hapus buku dari daftar |
| `statistik` | Ringkasan bacaanmu |
| `target [JUMLAH] [--tahun TAHUN]` | Atur atau lihat target baca tahunan |
| `sesi [--jumlah N]` | Lihat riwayat sesi baca terakhir (bawaan: 10) |
| `ekspor [BERKAS]` | Ekspor daftar buku ke berkas CSV (bawaan: daftar-buku.csv) |
| `--version` | Tampilkan versi CatatBuku |

## Status buku

Status berubah otomatis mengikuti progres halaman:

- **ingin dibaca** — baru ditambahkan, belum mulai dibaca
- **sedang dibaca** — sudah ada progres halaman, belum tamat
- **selesai** — halaman dibaca sudah sama dengan total halaman

## Data tersimpan di mana

Data tersimpan di `~/.config/catatbuku/` (format JSON, bisa dibuka dan
dibaca langsung):

- `buku.json` — daftar buku beserta progresnya
- `target.json` — target baca per tahun
- `sesi.json` — riwayat sesi baca

Variabel lingkungan `CATATBUKU_DATA` bisa dipakai untuk menunjuk berkas
buku lain (target dan sesi ikut tersimpan di sampingnya), berguna saat
menjalankan test.

## Rencana

- [x] Day-1: tambah buku, daftar buku, catat progres (status otomatis),
      perintah `hapus` + `statistik`, unit test, README lengkap
- [x] Day-2: target baca tahunan
- [x] Day-2: riwayat sesi baca
- [x] Day-2: ekspor (CSV)

## Menjalankan test

```bash
python3 -m unittest discover -s tests
```

95 test, semua lolos — unit test model dan end-to-end CLI (memakai
`CATATBUKU_DATA` ke berkas sementara supaya data asli tidak tersentuh):

- `tests/test_buku.py` (23) — model buku: tambah, progres, status, statistik
- `tests/test_cli.py` (23) — perintah CLI end-to-end
- `tests/test_target.py` (26) — target tahunan
- `tests/test_sesi.py` (17) — riwayat sesi baca
- `tests/test_ekspor.py` (6) — ekspor CSV

## Lisensi

MIT — lihat `LICENSE`.
