"""Module processor: logika pengolahan data inventaris (tanpa I/O)."""


def hapus_duplikat(daftar):
    """Menghapus record duplikat berdasarkan 'kode' (kemunculan pertama dipertahankan).

    Parameter:
        daftar (list[dict]): record bersih.
    Return:
        tuple: (unik, duplikat), keduanya list[dict].
    """
    sudah_ada = set()  # SET: cek keberadaan kode dalam O(1)
    unik, duplikat = [], []
    for barang in daftar:
        if barang["kode"] in sudah_ada:
            duplikat.append(barang)
        else:
            sudah_ada.add(barang["kode"])
            unik.append(barang)
    return unik, duplikat


def cari_barang(daftar, kata_kunci):
    """Mencari barang berdasarkan kata kunci pada kode atau nama (tidak peka huruf besar).

    Parameter:
        daftar (list[dict]): data barang.
        kata_kunci (str): teks yang dicari.
    Return:
        list[dict]: barang yang cocok (kosong jika tidak ada / kata kunci kosong).
    """
    kunci = kata_kunci.strip().lower()
    if not kunci:
        return []
    return [b for b in daftar
            if kunci in b["nama"].lower() or kunci in b["kode"].lower()]


def filter_kategori(daftar, kategori):
    """Menyaring barang berdasarkan kategori.

    Parameter:
        daftar (list[dict]): data barang.
        kategori (str): nama kategori (tidak peka huruf besar).
    Return:
        list[dict]: barang pada kategori tersebut.
    """
    target = kategori.strip().lower()
    return [b for b in daftar if b["kategori"].lower() == target]


def daftar_kategori(daftar):
    """Mengambil kategori unik yang ada pada data.

    Parameter:
        daftar (list[dict]): data barang.
    Return:
        list[str]: kategori unik terurut abjad.
    """
    return sorted({b["kategori"] for b in daftar})  # set comprehension


def kelompokkan_per_kategori(daftar):
    """Mengelompokkan barang menurut kategori.

    Parameter:
        daftar (list[dict]): data barang.
    Return:
        dict[str, list[dict]]: kategori -> daftar barang.
    """
    kelompok = {}  # DICT: kunci kategori -> list barang
    for barang in daftar:
        kelompok.setdefault(barang["kategori"], []).append(barang)
    return kelompok


def hitung_nilai(barang):
    """Menghitung nilai aset satu barang (jumlah x harga).

    Parameter:
        barang (dict): satu record barang.
    Return:
        int: nilai aset dalam rupiah.
    """
    return barang["jumlah"] * barang["harga"]


def rekap_per_kategori(daftar):
    """Membuat rekapitulasi jenis, total unit, dan total nilai per kategori.

    Parameter:
        daftar (list[dict]): data barang.
    Return:
        dict[str, dict]: kategori -> {jenis_barang, total_unit, total_nilai}.
    """
    kelompok = kelompokkan_per_kategori(daftar)
    return {  # dictionary comprehension
        kategori: {
            "jenis_barang": len(item),
            "total_unit": sum(b["jumlah"] for b in item),
            "total_nilai": sum(hitung_nilai(b) for b in item),
        }
        for kategori, item in sorted(kelompok.items())
    }


def total_nilai_aset(daftar):
    """Menjumlahkan nilai aset seluruh barang (0 jika data kosong).

    Parameter:
        daftar (list[dict]): data barang.
    Return:
        int: total nilai aset.
    """
    return sum(hitung_nilai(b) for b in daftar)


def status_stok(jumlah, batas_kritis):
    """Menentukan status stok.

    Parameter:
        jumlah (int): stok saat ini.
        batas_kritis (int): batas stok dianggap kritis.
    Return:
        str: 'HABIS', 'KRITIS', atau 'AMAN'.
    """
    if jumlah == 0:
        return "HABIS"
    elif jumlah <= batas_kritis:
        return "KRITIS"
    else:
        return "AMAN"


def stok_kritis(daftar, batas_kritis):
    """Mengambil barang yang stoknya HABIS atau KRITIS, terurut dari stok terkecil.

    Parameter:
        daftar (list[dict]): data barang.
        batas_kritis (int): batas stok kritis.
    Return:
        list[dict]: barang yang perlu dibeli ulang.
    """
    kritis = [b for b in daftar if status_stok(b["jumlah"], batas_kritis) != "AMAN"]
    return sorted(kritis, key=lambda b: (b["jumlah"], b["kode"]))
