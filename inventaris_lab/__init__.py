"""Package inventaris_lab: pengolahan data inventaris komponen laboratorium.

Module:
    validator    - validasi & pembersihan data (tidak bergantung module lain)
    processor    - logika pengolahan data (tidak bergantung module lain)
    report       - format teks laporan (bergantung pada processor)
    file_handler - baca/tulis CSV & JSON (bergantung pada validator)
"""

__version__ = "1.0.0"
__all__ = ["validator", "processor", "report", "file_handler"]
