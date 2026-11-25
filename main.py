"""Entry point CLI: Sistem Inventaris Laboratorium Teknik Komputer.

Mode interaktif : python main.py
Mode otomatis   : python main.py --input data/inventaris_lab.csv --otomatis
"""

import argparse
import json
import sys
from pathlib import Path

from inventaris_lab import file_handler, processor, report, validator

INPUT_DEFAULT = Path("data") / "inventaris_lab.csv"
OUTPUT_DEFAULT = Path("output")
BATAS_KRITIS_DEFAULT = 5
KOLOM_BERSIH = ["kode", "nama", "kategori", "jumlah", "harga", "lokasi"]
MENU_VALID = {0, 1, 2, 3, 4, 5, 6, 7}

TEKS_MENU = """
===== INVENTARIS LAB TEKNIK KOMPUTER =====
1. Muat & bersihkan file data
2. Tampilkan semua barang
3. Cari barang (kode / nama)
4. Filter berdasarkan kategori
5. Rekapitulasi per kategori
6. Barang stok kritis
7. Simpan hasil ke folder output
0. Keluar"""


def buat_parser():
    """Membuat parser argumen command line.

    Return:
        argparse.ArgumentParser: parser dengan opsi --input, --output,
        --batas-kritis, dan --otomatis.
    """
    parser = argparse.ArgumentParser(
        description="Aplikasi pengolahan data inventaris laboratorium (CLI).")
    parser.add_argument("--input", default=str(INPUT_DEFAULT),
                        help="file input .csv/.json (default: %(default)s)")
    parser.add_argument("--output", default=str(OUTPUT_DEFAULT),
                        help="folder keluaran (default: %(default)s)")
    parser.add_argument("--batas-kritis", type=int, default=BATAS_KRITIS_DEFAULT,
                        help="batas stok kritis (default: %(default)s)")
    parser.add_argument("--otomatis", action="store_true",
                        help="proses & simpan tanpa menu interaktif")
    return parser


def muat_dan_bersihkan(path):
    """Membaca file, memvalidasi, lalu membuang duplikat.

    Parameter:
        path (str | Path): lokasi file input.
    Return:
        dict: 'jumlah_mentah', 'bersih', 'ditolak', 'duplikat'.
    Raises:
        FileNotFoundError, json.JSONDecodeError, ValueError, OSError.
    """
    mentah = file_handler.baca_data(path)
    valid, ditolak = validator.pisahkan_valid(mentah)
    unik, duplikat = processor.hapus_duplikat(valid)
    return {"jumlah_mentah": len(mentah), "bersih": unik,
            "ditolak": ditolak, "duplikat": duplikat}


def muat_aman(path):
    """Membungkus muat_dan_bersihkan dengan penanganan error yang ramah pengguna.

    Parameter:
        path (str | Path): lokasi file input.
    Return:
        dict | None: hasil pemrosesan, atau None jika gagal (pesan sudah dicetak).
    """
    try:
        return muat_dan_bersihkan(path)
    except FileNotFoundError:
        print(f"[ERROR] File tidak ditemukan: {path}")
    except json.JSONDecodeError as galat:
        print(f"[ERROR] JSON rusak di baris {galat.lineno}, kolom {galat.colno}: {galat.msg}")
    except IsADirectoryError:
        print(f"[ERROR] '{path}' adalah folder, bukan file.")
    except PermissionError:
        print(f"[ERROR] Tidak punya izin membaca: {path}")
    except UnicodeDecodeError:
        print(f"[ERROR] Encoding file tidak valid (gunakan UTF-8): {path}")
    except ValueError as galat:
        print(f"[ERROR] Format data tidak valid: {galat}")
    except OSError as galat:
        print(f"[ERROR] Gagal membaca file: {galat}")
    return None


def simpan_hasil(hasil, folder, batas_kritis):
    """Menyimpan data bersih, rekap, log penolakan, dan laporan teks.

    Parameter:
        hasil (dict): keluaran muat_dan_bersihkan.
        folder (str | Path): folder keluaran.
        batas_kritis (int): batas stok kritis.
    Return:
        list[Path]: daftar file yang ditulis.
    """
    folder = Path(folder)
    bersih = hasil["bersih"]
    rekap = processor.rekap_per_kategori(bersih)
    kritis = processor.stok_kritis(bersih, batas_kritis)
    total = processor.total_nilai_aset(bersih)
    log_tolak = [{"baris": d["baris"], "alasan": d["alasan"],
                  "data_asli": json.dumps(d["data"], ensure_ascii=False)}
                 for d in hasil["ditolak"]]
    return [
        file_handler.simpan_csv(folder / "inventaris_bersih.csv", bersih, KOLOM_BERSIH),
        file_handler.simpan_json(folder / "rekap_kategori.json",
                                 {"total_nilai_aset": total, "rekap": rekap}),
        file_handler.simpan_csv(folder / "baris_ditolak.csv", log_tolak,
                                ["baris", "alasan", "data_asli"]),
        file_handler.simpan_teks(
            folder / "laporan_inventaris.txt",
            report.buat_laporan(hasil, rekap, kritis, total, batas_kritis)),
    ]


def simpan_aman(hasil, folder, batas_kritis):
    """Memanggil simpan_hasil dengan penanganan error penulisan file.

    Parameter:
        hasil (dict): keluaran muat_dan_bersihkan.
        folder (str | Path): folder keluaran.
        batas_kritis (int): batas stok kritis.
    Return:
        bool: True jika semua file tersimpan.
    """
    try:
        for path in simpan_hasil(hasil, folder, batas_kritis):
            print(f"  tersimpan: {path}")
        return True
    except OSError as galat:
        print(f"[ERROR] Gagal menyimpan hasil: {galat}")
        return False


def ringkas_hasil(hasil):
    """Mencetak ringkasan pembersihan data.

    Parameter:
        hasil (dict): keluaran muat_dan_bersihkan.
    Return:
        None
    """
    print(f"Dibaca {hasil['jumlah_mentah']} record -> {len(hasil['bersih'])} valid & unik, "
          f"{len(hasil['duplikat'])} duplikat, {len(hasil['ditolak'])} ditolak.")
    if not hasil["bersih"]:
        print("[PERINGATAN] Tidak ada data valid untuk diproses.")
    for d in hasil["ditolak"]:
        print(f"  - baris {d['baris']} ditolak: {d['alasan']}")


def baca_input(prompt):
    """Membaca input; EOF (Ctrl+D/Ctrl+Z) dianggap perintah keluar.

    Parameter:
        prompt (str): teks pertanyaan.
    Return:
        str: input pengguna.
    Raises:
        EOFError: bila input habis (ditangani di menu_interaktif).
    """
    return input(prompt)


def minta_pilihan_menu():
    """Meminta pilihan menu sampai pengguna memasukkan angka yang valid.

    Return:
        int: pilihan menu yang valid.
    """
    while True:
        print(TEKS_MENU)
        pilihan = validator.validasi_pilihan_menu(baca_input("Pilih menu [0-7]: "), MENU_VALID)
        if pilihan is not None:
            return pilihan
        print("[ERROR] Pilihan tidak valid. Masukkan angka 0-7.")


def menu_interaktif(path_awal, folder, batas_kritis):
    """Menjalankan loop menu interaktif.

    Parameter:
        path_awal (str): file input default.
        folder (str): folder keluaran.
        batas_kritis (int): batas stok kritis.
    Return:
        int: kode keluar (0 = normal).
    """
    hasil = None
    try:
        while True:
            pilihan = minta_pilihan_menu()
            if pilihan == 0:
                print("Terima kasih. Sampai jumpa!")
                return 0
            if pilihan == 1:
                path = baca_input(f"Path file [{path_awal}]: ").strip() or path_awal
                baru = muat_aman(path)
                if baru is not None:
                    hasil = baru
                    ringkas_hasil(hasil)
                continue
            if hasil is None:
                print("[ERROR] Data belum dimuat. Pilih menu 1 terlebih dahulu.")
                continue
            bersih = hasil["bersih"]
            if pilihan == 2:
                print(report.format_tabel(bersih, batas_kritis))
            elif pilihan == 3:
                kata = baca_input("Kata kunci (kode/nama): ")
                if not kata.strip():
                    print("[ERROR] Kata kunci tidak boleh kosong.")
                else:
                    print(report.format_tabel(processor.cari_barang(bersih, kata), batas_kritis))
            elif pilihan == 4:
                ada = processor.daftar_kategori(bersih)
                print("Kategori tersedia:", ", ".join(ada) if ada else "(kosong)")
                kat = baca_input("Nama kategori: ")
                if kat.strip().title() not in ada:
                    print(f"[ERROR] Kategori '{kat.strip()}' tidak ada pada data.")
                else:
                    print(report.format_tabel(processor.filter_kategori(bersih, kat), batas_kritis))
            elif pilihan == 5:
                print(report.format_rekap(processor.rekap_per_kategori(bersih)))
                print("Total nilai aset:", report.format_rupiah(processor.total_nilai_aset(bersih)))
            elif pilihan == 6:
                print(report.format_tabel(processor.stok_kritis(bersih, batas_kritis), batas_kritis))
            elif pilihan == 7:
                simpan_aman(hasil, folder, batas_kritis)
    except (EOFError, KeyboardInterrupt):
        print("\nProgram dihentikan pengguna.")
        return 0


def jalankan_otomatis(path, folder, batas_kritis):
    """Mode batch: muat, bersihkan, dan simpan tanpa interaksi.

    Parameter:
        path (str): file input.
        folder (str): folder keluaran.
        batas_kritis (int): batas stok kritis.
    Return:
        int: 0 jika sukses, 1 jika gagal.
    """
    hasil = muat_aman(path)
    if hasil is None:
        return 1
    ringkas_hasil(hasil)
    return 0 if simpan_aman(hasil, folder, batas_kritis) else 1


def main(argv=None):
    """Titik masuk program.

    Parameter:
        argv (list[str] | None): argumen CLI (None = sys.argv).
    Return:
        int: kode keluar proses.
    """
    args = buat_parser().parse_args(argv)
    if args.batas_kritis < 0:
        print("[ERROR] --batas-kritis tidak boleh negatif.")
        return 2
    if args.otomatis:
        return jalankan_otomatis(args.input, args.output, args.batas_kritis)
    return menu_interaktif(args.input, args.output, args.batas_kritis)


if __name__ == "__main__":
    sys.exit(main())
