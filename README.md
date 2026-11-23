# CatatBuku

Pencatat bacaan berbahasa Indonesia — kelola daftar buku, catat progres
halaman, dan lihat statistik bacaanmu. CLI Python, tanpa dependensi
eksternal, datamu tersimpan lokal di komputermu sendiri.

## Cara pakai

```bash
python3 -m catatbuku tambah "Laskar Pelangi" --penulis "Andrea Hirata" --halaman 529
python3 -m catatbuku daftar
python3 -m catatbuku progres 1 120
python3 -m catatbuku daftar --status sedang
```

| Perintah | Fungsi |
| --- | --- |
| `tambah JUDUL --penulis NAMA --halaman N` | Tambah buku baru ke daftar bacaan |
| `daftar [--status ingin\|sedang\|selesai]` | Lihat daftar buku beserta progresnya |
| `progres NOMOR HALAMAN` | Catat sudah sampai halaman berapa (status ikut berubah otomatis) |
| `statistik` | Ringkasan bacaanmu *(Day-2)* |
| `hapus NOMOR` | Hapus buku dari daftar *(Day-2)* |

Data tersimpan di `~/.config/catatbuku/buku.json`
(variabel lingkungan `CATATBUKU_DATA` bisa dipakai untuk menunjuk berkas lain,
berguna saat menjalankan test).

## Status buku

- **ingin dibaca** — baru ditambahkan, belum mulai dibaca
- **sedang dibaca** — sudah ada progres halaman, belum tamat
- **selesai** — halaman dibaca sudah sama dengan total halaman

## Rencana

- [x] Day-1: tambah buku, daftar buku, catat progres (status otomatis)
- [ ] Day-2: perintah `statistik` + `hapus` + unit test
- [ ] Day-2: README lengkap + versi 0.2.0

## Menjalankan test

```bash
python3 -m unittest discover -s tests
```

## Lisensi

MIT — lihat `LICENSE`.
