"""Module report: pemformatan teks tabel dan laporan (tanpa I/O file)."""

from datetime import datetime

from .processor import status_stok


def format_rupiah(angka):
    """Memformat bilangan menjadi 'Rp1.234.567'.

    Parameter:
        angka (int): nilai rupiah.
    Return:
        str: teks rupiah dengan pemisah titik.
    """
    return "Rp" + f"{angka:,}".replace(",", ".")


def format_tabel(daftar, batas_kritis=5):
    """Membuat tabel teks daftar barang.

    Parameter:
        daftar (list[dict]): data barang.
        batas_kritis (int): batas stok kritis untuk kolom status.
    Return:
        str: tabel siap cetak; pesan singkat jika data kosong.
    """
    if not daftar:
        return "(tidak ada data untuk ditampilkan)"
    baris = [f"{'KODE':<9}{'NAMA':<28}{'KATEGORI':<15}{'JML':>5} "
             f"{'HARGA':>12} {'STATUS':<7}LOKASI",
             "-" * 92]
    for b in daftar:
        baris.append(
            f"{b['kode']:<9}{b['nama'][:26]:<28}{b['kategori']:<15}{b['jumlah']:>5} "
            f"{format_rupiah(b['harga']):>12} "
            f"{status_stok(b['jumlah'], batas_kritis):<7}{b['lokasi']}"
        )
    return "\n".join(baris)


def format_rekap(rekap):
    """Membuat tabel teks rekapitulasi per kategori.

    Parameter:
        rekap (dict): keluaran processor.rekap_per_kategori.
    Return:
        str: tabel rekap; pesan singkat jika kosong.
    """
    if not rekap:
        return "(rekap kosong: tidak ada data valid)"
    baris = [f"{'KATEGORI':<15}{'JENIS':>6}{'UNIT':>8}{'TOTAL NILAI':>18}",
             "-" * 47]
    for kategori, nilai in rekap.items():
        baris.append(f"{kategori:<15}{nilai['jenis_barang']:>6}"
                     f"{nilai['total_unit']:>8}"
                     f"{format_rupiah(nilai['total_nilai']):>18}")
    return "\n".join(baris)


def buat_laporan(hasil, rekap, kritis, total_aset, batas_kritis):
    """Menyusun laporan lengkap hasil pemrosesan.

    Parameter:
        hasil (dict): berisi 'jumlah_mentah', 'bersih', 'ditolak', 'duplikat'.
        rekap (dict): rekap per kategori.
        kritis (list[dict]): barang stok kritis.
        total_aset (int): total nilai aset.
        batas_kritis (int): batas stok kritis.
    Return:
        str: isi laporan teks.
    """
    stempel = datetime.now().strftime("%Y-%m-%d %H:%M")
    bagian = [
        "LAPORAN INVENTARIS LABORATORIUM TEKNIK KOMPUTER",
        f"Dibuat: {stempel}",
        "=" * 60,
        f"Record dibaca        : {hasil['jumlah_mentah']}",
        f"Record valid & unik  : {len(hasil['bersih'])}",
        f"Duplikat dibuang     : {len(hasil['duplikat'])}",
        f"Record ditolak       : {len(hasil['ditolak'])}",
        f"Total nilai aset     : {format_rupiah(total_aset)}",
        "",
        "REKAP PER KATEGORI",
        format_rekap(rekap),
        "",
        f"BARANG STOK KRITIS (stok <= {batas_kritis})",
        format_tabel(kritis, batas_kritis),
    ]
    if hasil["duplikat"]:
        bagian += ["", "KODE DUPLIKAT: " +
                   ", ".join(b["kode"] for b in hasil["duplikat"])]
    if hasil["ditolak"]:
        bagian += ["", "RECORD DITOLAK"]
        bagian += [f"  baris {d['baris']}: {d['alasan']}" for d in hasil["ditolak"]]
    return "\n".join(bagian) + "\n"
