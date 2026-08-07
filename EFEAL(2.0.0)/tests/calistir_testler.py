#!/usr/bin/env python3
"""
Tüm EFEAI testlerini çalıştırır.
Kullanım: python tests/calistir_testler.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    from tests.test_brain       import calistir_tum_testler as brain_testleri
    from tests.test_database    import calistir_tum_testler as db_testleri
    from tests.test_code_engine import calistir_tum_testler as kod_testleri

    print("\n" + "═" * 50)
    print("   EFEAI — Tam Test Süiti")
    print("═" * 50)

    sonuclar = [
        ("Brain",       brain_testleri()),
        ("Veritabanı",  db_testleri()),
        ("Kod Motoru",  kod_testleri()),
    ]

    print("\n" + "═" * 50)
    print("   Genel Sonuç")
    print("═" * 50)
    hepsi_basarili = True
    for isim, basarili in sonuclar:
        durum = "✅ GEÇTI" if basarili else "❌ BAŞARISIZ"
        print(f"  {isim:<15}: {durum}")
        if not basarili:
            hepsi_basarili = False

    print()
    if hepsi_basarili:
        print("🎉 Tüm testler başarıyla geçti!")
    else:
        print("⚠️  Bazı testler başarısız. Lütfen hataları incele.")
    print()
    sys.exit(0 if hepsi_basarili else 1)


if __name__ == "__main__":
    main()
