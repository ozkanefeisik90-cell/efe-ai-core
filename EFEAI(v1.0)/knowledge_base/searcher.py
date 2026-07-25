"""
EFEAI Arama Motoru — Bilgi Tabanı Araştırıcı
JSON dosyalarını arar, ilgili konuları ve etiketleri döner.
Anahtar kelime eşleşmesi + anlam ilişkisi kurarak çalışır.
"""

import json
import re
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


# Eş anlamlı kelimeler — Türkçe/İngilizce çapraz arama
ESANLAMLILAR = {
    "döngü": ["loop", "for", "while", "iteration", "tekrar"],
    "loop": ["döngü", "for", "while", "tekrar"],
    "fonksiyon": ["function", "def", "metot", "method"],
    "function": ["fonksiyon", "def", "metot"],
    "liste": ["list", "array", "dizi"],
    "list": ["liste", "dizi"],
    "sözlük": ["dictionary", "dict", "json"],
    "dictionary": ["sözlük", "dict"],
    "hata": ["error", "exception", "bug", "sorun"],
    "error": ["hata", "exception", "bug"],
    "etiket": ["tag", "element"],
    "tag": ["etiket", "element"],
    "bağlantı": ["link", "href", "a"],
    "görsel": ["image", "img", "resim", "fotoğraf"],
    "form": ["input", "textarea", "button", "select"],
    "stil": ["style", "css"],
    "başlık": ["title", "heading", "h1", "h2", "h3"],
    "paragraf": ["paragraph", "p"],
    "tablo": ["table", "grid", "tr", "td", "th"],
    "sınıf": ["class", "oop"],
    "nesne": ["object", "instance"],
    "değişken": ["variable", "var", "değer"],
    "koşul": ["condition", "if", "else", "elif"],
    "algoritma": ["algorithm", "mantık"],
}


def mevcut_konular() -> list:
    """Bilgi tabanındaki mevcut tüm konuları listeler."""
    konular = []
    for dosya in DATA_DIR.glob("*.json"):
        try:
            with open(dosya, encoding="utf-8") as f:
                data = json.load(f)
            konular.append({
                "dosya": dosya.name,
                "konu": data.get("topic", dosya.stem),
                "zorluk": data.get("difficulty", "Belirsiz"),
                "tanim_sayisi": len(data.get("definitions", [])),
                "etiket_sayisi": len(data.get("tags", [])),
                "ornek_sayisi": len(data.get("examples", [])),
            })
        except Exception:
            pass
    return konular


def _dosya_yukle(dosya_adi: str) -> Optional[dict]:
    """JSON dosyasını yükler."""
    yol = DATA_DIR / dosya_adi
    if not yol.exists():
        return None
    try:
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _konu_dosyasi_bul(konu: str) -> Optional[str]:
    """Konu adına göre JSON dosyasını bulur."""
    konu_lower = konu.lower().strip()
    for dosya in DATA_DIR.glob("*.json"):
        try:
            with open(dosya, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("topic", "").lower() == konu_lower:
                return dosya.name
            # Dosya adı da kontrol et
            if dosya.stem.lower() == konu_lower:
                return dosya.name
        except Exception:
            pass
    return None


def _anahtar_kelime_puanla(metin: str, sorgu_kelimeleri: list) -> float:
    """Metne göre anahtar kelime eşleşme puanı hesaplar."""
    if not metin:
        return 0.0
    metin_lower = metin.lower()
    puan = 0.0
    for kelime in sorgu_kelimeleri:
        if kelime in metin_lower:
            puan += 1.0
        # Kısmi eşleşme
        elif any(kelime in k for k in metin_lower.split()):
            puan += 0.5
    return puan


def _genis_arama_kelimeleri(sorgu: str) -> list:
    """Eş anlamlıları da dahil ederek geniş arama kelime listesi oluşturur."""
    kelimeler = re.findall(r'\w+', sorgu.lower())
    genis = set(kelimeler)
    for kelime in kelimeler:
        if kelime in ESANLAMLILAR:
            genis.update(ESANLAMLILAR[kelime])
    return list(genis)


def genel_arama(sorgu: str, limit: int = 5) -> list:
    """
    Tüm bilgi tabanında arama yapar.
    Tanımlar, etiketler, örnekler ve ipuçları içinde arar.
    """
    if not sorgu.strip():
        return []

    kelimeler = _genis_arama_kelimeleri(sorgu)
    sonuclar = []

    for dosya in DATA_DIR.glob("*.json"):
        veri = _dosya_yukle(dosya.name)
        if not veri:
            continue

        konu = veri.get("topic", dosya.stem)

        # Tanımlarda ara
        for tanim in veri.get("definitions", []):
            arama_metni = f"{tanim.get('title','')} {tanim.get('content','')} {' '.join(tanim.get('keywords',[]))}"
            puan = _anahtar_kelime_puanla(arama_metni, kelimeler)
            if puan > 0:
                sonuclar.append({
                    "tip": "tanim",
                    "konu": konu,
                    "baslik": tanim.get("title", ""),
                    "icerik": tanim.get("content", ""),
                    "zorluk": tanim.get("difficulty", ""),
                    "puan": puan,
                })

        # Etiketlerde (HTML tags vb.) ara
        for etiket in veri.get("tags", []):
            arama_metni = f"{etiket.get('name','')} {etiket.get('description','')} {etiket.get('category','')}"
            puan = _anahtar_kelime_puanla(arama_metni, kelimeler)
            if puan > 0:
                sonuclar.append({
                    "tip": "etiket",
                    "konu": konu,
                    "baslik": etiket.get("name", ""),
                    "icerik": etiket.get("description", ""),
                    "ornek": etiket.get("example", ""),
                    "kategori": etiket.get("category", ""),
                    "puan": puan,
                })

        # Hatalarda ara
        for hata in veri.get("errors", []):
            arama_metni = f"{hata.get('problem','')} {hata.get('solution','')}"
            puan = _anahtar_kelime_puanla(arama_metni, kelimeler)
            if puan > 0:
                sonuclar.append({
                    "tip": "hata",
                    "konu": konu,
                    "baslik": hata.get("problem", ""),
                    "icerik": hata.get("solution", ""),
                    "yanlis": hata.get("wrong_example", ""),
                    "dogru": hata.get("correct_example", ""),
                    "puan": puan,
                })

        # Örneklerde ara
        for ornek in veri.get("examples", []):
            arama_metni = f"{ornek.get('title','')} {ornek.get('description','')}"
            puan = _anahtar_kelime_puanla(arama_metni, kelimeler)
            if puan > 0:
                sonuclar.append({
                    "tip": "ornek",
                    "konu": konu,
                    "baslik": ornek.get("title", ""),
                    "icerik": ornek.get("description", ""),
                    "kod": ornek.get("code", ""),
                    "puan": puan,
                })

        # İpuçlarında ara
        for ipucu in veri.get("tips", []):
            puan = _anahtar_kelime_puanla(ipucu, kelimeler)
            if puan > 0:
                sonuclar.append({
                    "tip": "ipucu",
                    "konu": konu,
                    "baslik": "İpucu",
                    "icerik": ipucu,
                    "puan": puan,
                })

    # Puana göre sırala
    sonuclar.sort(key=lambda x: x["puan"], reverse=True)
    return sonuclar[:limit]


def konu_detayi(konu: str) -> Optional[dict]:
    """Belirli bir konu hakkında tüm bilgileri döner."""
    dosya = _konu_dosyasi_bul(konu)
    if not dosya:
        return None
    return _dosya_yukle(dosya)


def etiket_ara(konu: str, etiket_adi: str) -> Optional[dict]:
    """Belirli bir konudaki belirli etiketi/öğeyi bulur."""
    veri = konu_detayi(konu)
    if not veri:
        return None

    etiket_lower = etiket_adi.lower().strip()
    for etiket in veri.get("tags", []):
        if etiket.get("name", "").lower().strip("<>") == etiket_lower.strip("<>"):
            return etiket
    return None


def hata_ara(konu: str, sorun: str) -> list:
    """Belirli bir konudaki hataları arar."""
    veri = konu_detayi(konu)
    if not veri:
        return []

    kelimeler = _genis_arama_kelimeleri(sorun)
    sonuclar = []
    for hata in veri.get("errors", []):
        arama_metni = f"{hata.get('problem','')} {hata.get('solution','')}"
        puan = _anahtar_kelime_puanla(arama_metni, kelimeler)
        if puan > 0:
            sonuclar.append({**hata, "puan": puan})
    sonuclar.sort(key=lambda x: x["puan"], reverse=True)
    return sonuclar


def ornek_al(konu: str, baslik: str = None) -> list:
    """Belirli bir konudaki örnekleri döner."""
    veri = konu_detayi(konu)
    if not veri:
        return []

    ornekler = veri.get("examples", [])
    if baslik:
        baslik_lower = baslik.lower()
        ornekler = [o for o in ornekler if baslik_lower in o.get("title", "").lower()]
    return ornekler


def ipuclari_al(konu: str) -> list:
    """Belirli konunun ipuçlarını döner."""
    veri = konu_detayi(konu)
    if not veri:
        return []
    return veri.get("tips", [])


def ilgili_konular(konu: str) -> list:
    """İlgili konuları döner."""
    veri = konu_detayi(konu)
    if not veri:
        return []
    return veri.get("related_topics", [])
