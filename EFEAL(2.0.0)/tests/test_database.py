"""
EFEAI Veritabanı Testleri
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def _db_hazirla():
    """Test için veritabanını hazırlar."""
    from database import db
    db.tablolari_olustur()


def test_tablo_olusturma():
    _db_hazirla()
    print("✅ test_tablo_olusturma geçti")


def test_konusma_kaydet():
    from database import db
    _db_hazirla()
    db.konusma_kaydet("test_session", "user", "Test mesajı", topic="Python")
    gecmis = db.konusma_gecmisi(limit=1)
    assert len(gecmis) >= 1
    print("✅ test_konusma_kaydet geçti")


def test_proje_olustur_ve_listele():
    from database import db
    _db_hazirla()
    pid = db.proje_olustur("Test Proje", "Açıklama", "Python", ["Flask"], "Web Uygulaması")
    assert isinstance(pid, int) and pid > 0

    projeler = db.proje_listele()
    assert any(p["name"] == "Test Proje" for p in projeler)
    print("✅ test_proje_olustur_ve_listele geçti")


def test_proje_guncelle():
    from database import db
    _db_hazirla()
    pid = db.proje_olustur("Güncellenecek Proje", "", "JavaScript", [], "Web")
    basarili = db.proje_guncelle(pid, progress=75, status="Geliştiriliyor")
    assert basarili

    proje = db.proje_al(pid)
    assert proje["progress"] == 75
    assert proje["status"] == "Geliştiriliyor"
    print("✅ test_proje_guncelle geçti")


def test_gorev_ekle_ve_tamamla():
    from database import db
    _db_hazirla()
    pid = db.proje_olustur("Görev Test Proje", "", "Python", [], "API")
    gid = db.gorev_ekle(pid, "Test Görevi", "yüksek")
    assert isinstance(gid, int) and gid > 0

    basarili = db.gorev_tamamla(gid)
    assert basarili

    gorevler = db.proje_gorevleri(pid)
    tamamlanan = [g for g in gorevler if g["done"]]
    assert len(tamamlanan) >= 1
    print("✅ test_gorev_ekle_ve_tamamla geçti")


def test_not_ekle_ve_listele():
    from database import db
    _db_hazirla()
    nid = db.not_ekle("Test Not", "Bu bir test notudur.", ["test", "python"])
    assert isinstance(nid, int) and nid > 0

    notlar = db.not_listele()
    assert any(n["title"] == "Test Not" for n in notlar)
    print("✅ test_not_ekle_ve_listele geçti")


def test_not_ara():
    from database import db
    _db_hazirla()
    db.not_ekle("Arama Test Notu", "Python listeleri hakkında not.", ["python"])
    sonuclar = db.not_ara("Python")
    assert len(sonuclar) >= 1
    print("✅ test_not_ara geçti")


def test_ogrenme_ilerlemesi():
    from database import db
    _db_hazirla()
    db.ogrenme_ilerlemesi_kaydet("Python", durum="Öğreniliyor", sure_dk=30)
    harita = db.ogrenme_haritasi()
    python_kayit = [k for k in harita if k.get("topic") == "Python"]
    assert len(python_kayit) >= 1
    print("✅ test_ogrenme_ilerlemesi geçti")


def test_genel_istatistikler():
    from database import db
    _db_hazirla()
    stats = db.genel_istatistikler()
    assert "proje_sayisi" in stats
    assert "not_sayisi" in stats
    assert "toplam_mesaj" in stats
    print("✅ test_genel_istatistikler geçti")


def calistir_tum_testler():
    testler = [
        test_tablo_olusturma,
        test_konusma_kaydet,
        test_proje_olustur_ve_listele,
        test_proje_guncelle,
        test_gorev_ekle_ve_tamamla,
        test_not_ekle_ve_listele,
        test_not_ara,
        test_ogrenme_ilerlemesi,
        test_genel_istatistikler,
    ]

    basarili = 0
    basarisiz = 0

    print("\n═══ EFEAI Veritabanı Testleri ═══\n")
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
