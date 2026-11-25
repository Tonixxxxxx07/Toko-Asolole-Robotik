"""Module file_handler: membaca dan menulis file CSV / JSON."""

import csv
import json
from pathlib import Path

from .validator import KOLOM_WAJIB


def _normalkan_kunci(baris):
    """Membuat kunci dict menjadi huruf kecil tanpa spasi tepi.

    Parameter:
        baris (dict): satu record mentah.
    Return:
        dict: record dengan kunci ternormalisasi.
    """
    return {str(k or "").strip().lower(): v for k, v in baris.items()}


def baca_csv(path):
    """Membaca file CSV menjadi list of dict.

    Parameter:
        path (str | Path): lokasi file CSV.
    Return:
        list[dict]: record mentah (bisa kosong jika hanya ada header).
    Raises:
        FileNotFoundError: file tidak ada.
        ValueError: file kosong / header tidak lengkap / encoding salah.
    """
    with open(path, newline="", encoding="utf-8-sig") as berkas:
        pembaca = csv.DictReader(berkas)
        if pembaca.fieldnames is None:
            raise ValueError("file CSV kosong (tidak ada header)")
        header = {str(h or "").strip().lower() for h in pembaca.fieldnames}
        kurang = sorted(set(KOLOM_WAJIB) - header)
        if kurang:
            raise ValueError("kolom wajib tidak ditemukan: " + ", ".join(kurang))
        return [_normalkan_kunci(baris) for baris in pembaca]


def baca_json(path):
    """Membaca file JSON berisi list of object.

    Parameter:
        path (str | Path): lokasi file JSON.
    Return:
        list[dict]: record mentah.
    Raises:
        FileNotFoundError: file tidak ada.
        json.JSONDecodeError: isi JSON rusak.
        ValueError: struktur bukan list of object.
    """
    with open(path, encoding="utf-8-sig") as berkas:
        isi = json.load(berkas)
    if not isinstance(isi, list):
        raise ValueError("JSON harus berupa list of object")
    if not all(isinstance(item, dict) for item in isi):
        raise ValueError("setiap elemen JSON harus berupa object")
    return [_normalkan_kunci(item) for item in isi]


def baca_data(path):
    """Memilih pembaca file berdasarkan ekstensi (.csv / .json).

    Parameter:
        path (str | Path): lokasi file input.
    Return:
        list[dict]: record mentah.
    Raises:
        IsADirectoryError: path berupa folder.
        ValueError: ekstensi tidak didukung (+ error dari pembaca terkait).
    """
    if Path(path).is_dir():
        raise IsADirectoryError(f"'{path}' adalah folder")
    ekstensi = Path(path).suffix.lower()
    if ekstensi == ".csv":
        return baca_csv(path)
    if ekstensi == ".json":
        return baca_json(path)
    raise ValueError(f"ekstensi '{ekstensi}' tidak didukung (gunakan .csv atau .json)")


def _siapkan_folder(path):
    """Membuat folder induk file tujuan bila belum ada.

    Parameter:
        path (str | Path): lokasi file tujuan.
    Return:
        Path: objek Path file tujuan.
    """
    tujuan = Path(path)
    tujuan.parent.mkdir(parents=True, exist_ok=True)
    return tujuan


def simpan_csv(path, daftar, kolom):
    """Menyimpan list of dict ke file CSV.

    Parameter:
        path (str | Path): lokasi file keluaran.
        daftar (list[dict]): data yang disimpan.
        kolom (list[str]): urutan kolom.
    Return:
        Path: lokasi file yang ditulis.
    """
    tujuan = _siapkan_folder(path)
    with open(tujuan, "w", newline="", encoding="utf-8") as berkas:
        penulis = csv.DictWriter(berkas, fieldnames=kolom, extrasaction="ignore")
        penulis.writeheader()
        penulis.writerows(daftar)
    return tujuan


def simpan_json(path, data):
    """Menyimpan data ke file JSON (indentasi 2, mendukung karakter non-ASCII).

    Parameter:
        path (str | Path): lokasi file keluaran.
        data: objek yang dapat diserialisasi JSON.
    Return:
        Path: lokasi file yang ditulis.
    """
    tujuan = _siapkan_folder(path)
    with open(tujuan, "w", encoding="utf-8") as berkas:
        json.dump(data, berkas, indent=2, ensure_ascii=False)
    return tujuan


def simpan_teks(path, teks):
    """Menyimpan teks ke file.

    Parameter:
        path (str | Path): lokasi file keluaran.
        teks (str): isi file.
    Return:
        Path: lokasi file yang ditulis.
    """
    tujuan = _siapkan_folder(path)
    with open(tujuan, "w", encoding="utf-8") as berkas:
        berkas.write(teks)
    return tujuan
