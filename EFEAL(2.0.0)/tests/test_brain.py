"""
EFEAI Brain Modülü Testleri
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_intent_selamlama():
    from core.intent import intent_tespit_et, Intent
    sonuc = intent_tespit_et("merhaba")
    assert sonuc["intent"] == Intent.SELAMLAMA, f"Beklenen: selamlama, Gelen: {sonuc['intent']}"
    print("✅ test_intent_selamlama geçti")


def test_intent_bilgi_ara():
    from core.intent import intent_tespit_et, Intent
    sonuc = intent_tespit_et("Python nedir")
    assert sonuc["intent"] in (Intent.BILGI_ARA, Intent.GENEL_ARAMA)
    print("✅ test_intent_bilgi_ara geçti")


def test_intent_kod_analiz():
    from core.intent import intent_tespit_et, Intent
    kod_mesaji = "```python\ndef test():\n    pass\n```"
    sonuc = intent_tespit_et(kod_mesaji)
    assert sonuc["intent"] == Intent.KOD_ANALIZ
    print("✅ test_intent_kod_analiz geçti")


def test_intent_veda():
    from core.intent import intent_tespit_et, Intent
    sonuc = intent_tespit_et("görüşürüz")
    assert sonuc["intent"] == Intent.VEDA
    print("✅ test_intent_veda geçti")


def test_konu_cikar_python():
    from core.intent import konu_cikar
    konu = konu_cikar("Python nedir")
    assert konu is not None
    assert "Python" in konu
    print("✅ test_konu_cikar_python geçti")


def test_character_engine_normal():
    from core.character_engine import CharacterEngine, ConversationMode
    karakter = CharacterEngine(mode=ConversationMode.NORMAL)
    acilis = karakter.acilis_cumle()
    assert isinstance(acilis, str)
    assert len(acilis) > 0
    print("✅ test_character_engine_normal geçti")


def test_character_engine_samimi():
    from core.character_engine import CharacterEngine, ConversationMode
    karakter = CharacterEngine(mode=ConversationMode.SAMIMI)
    # 3 mesaj sonra samimi açılış gelmeli
    for _ in range(3):
        karakter.acilis_cumle()
    acilis = karakter.acilis_cumle()
    assert isinstance(acilis, str)
    print("✅ test_character_engine_samimi geçti")


def test_bilmiyorum_yaniti():
    from core.character_engine import CharacterEngine
    karakter = CharacterEngine()
    yanit = karakter.bilmiyorum_yaniti()
    assert "bilgi" in yanit.lower() or "konuda" in yanit.lower()
    print("✅ test_bilmiyorum_yaniti geçti")


def test_memory_ekle_ve_getir():
    from core.memory import Memory
    hafıza = Memory("test_session_001")
    hafıza.ekle("user", "Python nedir?", konu="Python")
    hafıza.ekle("efeai", "Python bir programlama dilidir.", konu="Python")

    son = hafıza.son_mesajlar(5)
    assert len(son) == 2
    assert son[0]["mesaj"] == "Python nedir?"
    assert hafıza.son_konu() == "Python"
    print("✅ test_memory_ekle_ve_getir geçti")


def test_memory_ozet():
    from core.memory import Memory
    hafıza = Memory("test_session_002")
    hafıza.ekle("user", "Merhaba")
    hafıza.ekle("efeai", "Merhaba! Nasıl yardımcı olabilirim?")
    ozet = hafıza.oturum_ozeti()
    assert ozet["kullanici_mesaj"] == 1
    assert ozet["efeai_mesaj"] == 1
    print("✅ test_memory_ozet geçti")


def calistir_tum_testler():
    testler = [
        test_intent_selamlama,
        test_intent_bilgi_ara,
        test_intent_kod_analiz,
        test_intent_veda,
        test_konu_cikar_python,
        test_character_engine_normal,
        test_character_engine_samimi,
        test_bilmiyorum_yaniti,
        test_memory_ekle_ve_getir,
        test_memory_ozet,
    ]

    basarili = 0
    basarisiz = 0

    print("\n═══ EFEAI Brain Testleri ═══\n")
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
