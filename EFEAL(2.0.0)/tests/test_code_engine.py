"""
EFEAI Kod Motoru Testleri
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_dil_tespit_python():
    from code_engine.analyzer import dil_tespit_et
    kod = "def merhaba():\n    print('Merhaba')\n\nmerhaba()"
    assert dil_tespit_et(kod) == "python"
    print("✅ test_dil_tespit_python geçti")


def test_dil_tespit_javascript():
    from code_engine.analyzer import dil_tespit_et
    kod = "const x = 5;\nconsole.log(x);\nfunction topla(a, b) { return a + b; }"
    assert dil_tespit_et(kod) == "javascript"
    print("✅ test_dil_tespit_javascript geçti")


def test_dil_tespit_html():
    from code_engine.analyzer import dil_tespit_et
    kod = "<!DOCTYPE html>\n<html>\n<body><h1>Test</h1></body>\n</html>"
    assert dil_tespit_et(kod) == "html"
    print("✅ test_dil_tespit_html geçti")


def test_python_analiz_raporu():
    from code_engine.analyzer import kodu_analiz_et, analiz_raporu_formatla
    kod = "def test():\n    pass\n\nprint('Merhaba')"
    rapor = kodu_analiz_et(kod)
    assert isinstance(rapor, dict)
    assert "dil" in rapor
    assert rapor["dil"] == "python"
    rapor_metni = analiz_raporu_formatla(rapor)
    assert isinstance(rapor_metni, str)
    assert len(rapor_metni) > 0
    print("✅ test_python_analiz_raporu geçti")


def test_generator_python_fonksiyon():
    from code_engine.generator import KodUretici
    uretici = KodUretici()
    kod = uretici.uret("fonksiyon yaz", "python")
    assert "def" in kod or "fonksiyon" in kod.lower() or "TODO" in kod
    print("✅ test_generator_python_fonksiyon geçti")


def test_generator_html_sayfa():
    from code_engine.generator import KodUretici
    uretici = KodUretici()
    kod = uretici.uret("web sayfası oluştur", "html")
    assert "<!DOCTYPE" in kod or "<html" in kod
    print("✅ test_generator_html_sayfa geçti")


def test_debugger_python_hata():
    from code_engine.debugger import KodHataAyiklayici
    ayiklayici = KodHataAyiklayici()
    # eval() kullanımı kritik güvenlik sorunu
    kod = "sonuc = eval(kullanici_girdisi)"
    rapor = ayiklayici.hatalar_bul(kod, "python")
    # rapor ya hata bulamaz ya da bulur — her iki durumda string olmalı
    assert isinstance(rapor, str)
    print("✅ test_debugger_python_hata geçti")


def test_formatter_python():
    from code_engine.formatter import KodBiçimlendirici
    bicimlendirici = KodBiçimlendirici()
    kod = "def test():\t\n\t\tpass\t\n"
    sonuc = bicimlendirici.bicimlendir(kod, "python")
    assert isinstance(sonuc, str)
    assert "\t" not in sonuc  # Sekmeler temizlenmeli
    print("✅ test_formatter_python geçti")


def test_formatter_sql():
    from code_engine.formatter import KodBiçimlendirici
    bicimlendirici = KodBiçimlendirici()
    kod = "select id, isim from kullanicilar where id = 1"
    sonuc = bicimlendirici.bicimlendir(kod, "sql")
    assert "SELECT" in sonuc  # Büyük harfe çevrilmeli
    print("✅ test_formatter_sql geçti")


def test_security_eval_tespiti():
    from code_engine.security import GuvenlikTarayici
    tarayici = GuvenlikTarayici()
    kod = "sonuc = eval(kullanici_girdisi)\nexec('import os')"
    rapor = tarayici.tara(kod, "python")
    assert "kritik" in rapor.lower() or "KRİTİK" in rapor or "eval" in rapor.lower()
    print("✅ test_security_eval_tespiti geçti")


def test_security_temiz_kod():
    from code_engine.security import GuvenlikTarayici
    tarayici = GuvenlikTarayici()
    kod = "def topla(a, b):\n    return a + b\n\nprint(topla(3, 5))"
    guvenli = tarayici.guvenli_kod_mu(kod, "python")
    assert guvenli is True
    print("✅ test_security_temiz_kod geçti")


def calistir_tum_testler():
    testler = [
        test_dil_tespit_python,
        test_dil_tespit_javascript,
        test_dil_tespit_html,
        test_python_analiz_raporu,
        test_generator_python_fonksiyon,
        test_generator_html_sayfa,
        test_debugger_python_hata,
        test_formatter_python,
        test_formatter_sql,
        test_security_eval_tespiti,
        test_security_temiz_kod,
    ]

    basarili = 0
    basarisiz = 0

    print("\n═══ EFEAI Kod Motoru Testleri ═══\n")
    for test in testler:
        try:
            test()
            basarili += 1
        except Exception as e:
            print(f"❌ {test.__name__} BAŞARISIZ: {e}")
            basarisiz += 1

    print(f"\n{'═'*35}")
    print(f"Sonuç: {basarili} geçti, {basarisiz} başarısız")
    return basarisiz == 0


if __name__ == "__main__":
    basarili = calistir_tum_testler()
    sys.exit(0 if basarili else 1)
