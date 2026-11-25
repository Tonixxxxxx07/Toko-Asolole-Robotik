"""Module validator: validasi dan pembersihan data inventaris."""

KOLOM_WAJIB = ("kode", "nama", "kategori", "jumlah", "harga", "lokasi")

# SET: kumpulan kategori sah. Dipilih karena pengecekan keanggotaan O(1)
# dan tidak ada duplikat.
KATEGORI_VALID = {
    "mikrokontroler", "sensor", "aktuator", "komputer",
    "jaringan", "perkakas", "kabel",
}


def bersihkan_teks(nilai):
    """Mengubah nilai apa pun menjadi string tanpa spasi di tepi.

    Parameter:
        nilai: data mentah (str, int, float, None, dll).
    Return:
        str: teks bersih; string kosong jika nilai None.
    """
    if nilai is None:
        return ""
    return str(nilai).strip()


def ubah_ke_int(nilai, nama_kolom):
    """Mengubah nilai menjadi bilangan bulat dengan aman.

    Parameter:
        nilai: data mentah (mis. '25', 7.0, 'sepuluh').
        nama_kolom (str): nama kolom, dipakai untuk pesan error.
    Return:
        int: hasil konversi.
    Raises:
        ValueError: jika nilai bukan bilangan bulat.
    """
    teks = bersihkan_teks(nilai)
    try:
        return int(teks)
    except ValueError:
        pass
    try:
        angka = float(teks)
    except ValueError:
        raise ValueError(
            f"kolom '{nama_kolom}' harus angka, ditemukan '{teks}'"
        ) from None
    if angka.is_integer():  # mis. '7.0' dianggap 7
        return int(angka)
    raise ValueError(f"kolom '{nama_kolom}' harus bilangan bulat, ditemukan '{teks}'")


def validasi_baris(baris):
    """Memvalidasi satu baris data mentah dan menormalkannya.

    Aturan: kode & nama wajib terisi, kategori harus ada di KATEGORI_VALID,
    jumlah >= 0, harga >= 0, lokasi kosong diisi '-'.

    Parameter:
        baris (dict): satu record mentah.
    Return:
        dict: record bersih dengan tipe data yang benar.
    Raises:
        ValueError: jika ada aturan yang dilanggar (pesan = alasan).
    """
    kode = bersihkan_teks(baris.get("kode")).upper()
    nama = bersihkan_teks(baris.get("nama"))
    kategori = bersihkan_teks(baris.get("kategori")).lower()
    lokasi = bersihkan_teks(baris.get("lokasi")) or "-"

    if not kode:
        raise ValueError("kode barang kosong")
    if not nama:
        raise ValueError("nama barang kosong")
    if kategori not in KATEGORI_VALID:
        raise ValueError(f"kategori tidak dikenal: '{kategori}'")

    jumlah = ubah_ke_int(baris.get("jumlah"), "jumlah")
    harga = ubah_ke_int(baris.get("harga"), "harga")
    if jumlah < 0:
        raise ValueError(f"jumlah tidak boleh negatif ({jumlah})")
    if harga < 0:
        raise ValueError(f"harga tidak boleh negatif ({harga})")

    return {
        "kode": kode,
        "nama": nama,
        "kategori": kategori.title(),
        "jumlah": jumlah,
        "harga": harga,
        "lokasi": lokasi,
    }


def pisahkan_valid(daftar_mentah):
    """Memisahkan record valid dan record yang ditolak.

    Parameter:
        daftar_mentah (list[dict]): seluruh record mentah dari file.
    Return:
        tuple: (valid, ditolak)
            valid  : list[dict] record bersih
            ditolak: list[dict] berisi 'baris', 'alasan', 'data'
    """
    valid, ditolak = [], []
    # enumerate mulai 2: baris 1 pada CSV adalah header
    for nomor, baris in enumerate(daftar_mentah, start=2):
        try:
            valid.append(validasi_baris(baris))
        except ValueError as galat:
            ditolak.append({"baris": nomor, "alasan": str(galat), "data": baris})
    return valid, ditolak


def validasi_pilihan_menu(teks, pilihan_valid):
    """Memvalidasi input menu dari pengguna.

    Parameter:
        teks (str): input mentah dari keyboard.
        pilihan_valid (set[int]): angka menu yang diizinkan.
    Return:
        int | None: angka pilihan jika valid, None jika tidak valid.
    """
    teks = bersihkan_teks(teks)
    if not teks.isdigit():
        return None
    angka = int(teks)
    return angka if angka in pilihan_valid else None
