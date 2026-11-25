# Sistem Inventaris Laboratorium Teknik Komputer (CLI)

Aplikasi command line berbasis **Python 3 + standard library** untuk membersihkan,
mencari, memfilter, merekap, dan melaporkan data inventaris komponen laboratorium
dari file CSV/JSON. Proyek UTS Pemrograman Dasar (TK091), Universitas AMIKOM Yogyakarta.

## Struktur Direktori
```
uts_inventaris_lab/
├── main.py                     # entry point CLI (menu interaktif & mode otomatis)
├── README.md
├── LAPORAN_UTS.md              # lembar jawaban (konversi ke PDF)
├── inventaris_lab/             # package buatan sendiri
│   ├── __init__.py
│   ├── validator.py            # validasi & normalisasi data
│   ├── processor.py            # pencarian, filter, grouping, rekap, hapus duplikat
│   ├── report.py               # format tabel & laporan teks
│   └── file_handler.py         # baca/tulis CSV & JSON
├── data/                       # contoh input
│   ├── inventaris_lab.csv      # normal + duplikat + data kotor
│   ├── inventaris_tambahan.json
│   ├── inventaris_kosong.csv   # edge case: hanya header
│   ├── file_kosong_0byte.csv   # edge case: file 0 byte
│   └── inventaris_rusak.json   # edge case: JSON tidak valid
└── output/                     # contoh hasil
    ├── inventaris_bersih.csv
    ├── rekap_kategori.json
    ├── baris_ditolak.csv
    └── laporan_inventaris.txt
```

## Package & Library
- **Package buatan sendiri:** `inventaris_lab` (4 module).
- **Standard library:** `csv`, `json`, `argparse`, `pathlib`, `sys`, `datetime`.
- **Dependency pihak ketiga:** tidak ada. Tidak perlu `pip install`.

## Cara Menjalankan
Prasyarat: Python 3.8+ (`python --version`). Gunakan `python3` pada Linux/macOS.

1. Buka terminal/CMD, masuk ke folder proyek: `cd uts_inventaris_lab`
2. **Mode interaktif (menu):** `python main.py`
3. **Mode otomatis (batch):** `python main.py --otomatis`
4. Opsi: 
   ```
   python main.py --input data/inventaris_tambahan.json --output output/json --batas-kritis 5 --otomatis
   ```
   | Opsi | Fungsi | Default |
   |---|---|---|
   | `--input` | file .csv / .json | `data/inventaris_lab.csv` |
   | `--output` | folder keluaran | `output` |
   | `--batas-kritis` | stok <= nilai ini dianggap kritis | `5` |
   | `--otomatis` | proses & simpan tanpa menu | mati |

Menu interaktif: 1 Muat data, 2 Tampilkan, 3 Cari, 4 Filter kategori, 5 Rekap, 6 Stok kritis, 7 Simpan, 0 Keluar.
Jalankan menu **1** dahulu sebelum menu 2-7.

## Format Data
Input (CSV atau JSON list of object), kolom wajib: `kode, nama, kategori, jumlah, harga, lokasi`.
Kategori sah: Mikrokontroler, Sensor, Aktuator, Komputer, Jaringan, Perkakas, Kabel.

Output: `inventaris_bersih.csv`, `rekap_kategori.json`, `baris_ditolak.csv`, `laporan_inventaris.txt`.

## Skenario Pengujian
| Skenario | Perintah | Hasil yang diharapkan |
|---|---|---|
| Data normal + kotor | `python main.py --otomatis` | 25 dibaca -> 17 valid, 2 duplikat, 6 ditolak; total aset Rp42.004.000 |
| JSON | `python main.py --otomatis --input data/inventaris_tambahan.json --output output/json` | 5 dibaca -> 3 valid, 1 duplikat, 1 ditolak |
| Edge: hanya header | `python main.py --otomatis --input data/inventaris_kosong.csv --output output/kosong` | peringatan, tidak crash, total Rp0, exit 0 |
| Edge: file 0 byte | `python main.py --otomatis --input data/file_kosong_0byte.csv` | pesan "file CSV kosong", exit 1 |
| File tidak ada | `python main.py --otomatis --input data/x.csv` | "File tidak ditemukan", exit 1 |
| JSON rusak | `python main.py --otomatis --input data/inventaris_rusak.json` | pesan baris/kolom error, exit 1 |
| Input menu salah | `python main.py` lalu ketik `abc` | "Pilihan tidak valid", menu diulang |
