"""
EFEAI Arama Motoru — Bilgi Tabanı Araştırıcı
JSON dosyalarını arar, ilgili konuları ve etiketleri döner.
Anahtar kelime eşleşmesi + anlam ilişkisi kurarak çalışır.
Alt klasörlerdeki JSON dosyalarını da tarar.
"""

import json
import re
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"  # Eski uyumluluk için

# Tüm bilgi tabanı arama kökü (alt klasörler dahil)
KB_KOKU = BASE_DIR


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
    "güvenlik": ["security", "siber", "cyber"],
    "yapay zeka": ["ai", "ml", "makine öğrenmesi"],
    "flutter": ["dart", "mobil uygulama"],
    "git": ["versiyon", "branch", "commit", "repo"],
    "linux": ["terminal", "bash", "shell", "unix"],
}


def _tum_json_dosyalari() -> list:
    """Tüm bilgi tabanındaki JSON dosyalarını bulur (alt klasörler dahil)."""
    dosyalar = []
    # Eski data/ klasörü
    if DATA_DIR.exists():
        dosyalar.extend(DATA_DIR.glob("*.json"))
    # Yeni teknoloji alt klasörleri
    for alt_klasor in KB_KOKU.iterdir():
        if alt_klasor.is_dir() and alt_klasor.name not in ("data", "__pycache__"):
            dosyalar.extend(alt_klasor.glob("*.json"))
    return dosyalar


def mevcut_konular() -> list:
    """Bilgi tabanındaki mevcut tüm konuları listeler."""
    konular = []
    for dosya in _tum_json_dosyalari():
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
                "klasor": dosya.parent.name,
            })
        except Exception:
            pass
    return konular


def _dosya_yukle(dosya_yolu: Path) -> Optional[dict]:
    """JSON dosyasını yükler."""
    if not dosya_yolu.exists():
        return None
    try:
        with open(dosya_yolu, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _konu_dosyasi_bul(konu: str) -> Optional[Path]:
    """Konu adına göre JSON dosyasını bulur."""
    konu_lower = konu.lower().strip()
    for dosya in _tum_json_dosyalari():
        try:
            with open(dosya, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("topic", "").lower() == konu_lower:
                return dosya
            if dosya.stem.lower() == konu_lower:
                return dosya
            # Kısmi eşleşme — konu adı dosya/topic içinde geçiyorsa
            if konu_lower in data.get("topic", "").lower():
                return dosya
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
    """Tüm bilgi tabanında arama yapar."""
    kelimeler = _genis_arama_kelimeleri(sorgu)
    sonuclar = []

    for dosya in _tum_json_dosyalari():
        try:
            with open(dosya, encoding="utf-8") as f:
                data = json.load(f)

            puan = 0.0
            konu_adi = data.get("topic", "")
            puan += _anahtar_kelime_puanla(konu_adi, kelimeler) * 3

            for tanim in data.get("definitions", []):
                icerik = tanim.get("content", "") if isinstance(tanim, dict) else str(tanim)
                puan += _anahtar_kelime_puanla(icerik, kelimeler)

            for etiket in data.get("tags", []):
                etiket_adi = etiket.get("name", "") if isinstance(etiket, dict) else str(etiket)
                puan += _anahtar_kelime_puanla(etiket_adi, kelimeler) * 2

            if puan > 0:
                ilgili_tanim = ""
                tanımlar = data.get("definitions", [])
                if tanımlar:
                    ilk = tanımlar[0]
                    ilgili_tanim = ilk.get("content", "") if isinstance(ilk, dict) else str(ilk)

                sonuclar.append({
                    "konu": konu_adi,
                    "puan": puan,
                    "zorluk": data.get("difficulty", ""),
                    "ilgili_tanim": ilgili_tanim[:200] if ilgili_tanim else "",
                    "dosya": dosya.name,
                    "klasor": dosya.parent.name,
                })
        except Exception:
            pass

    sonuclar.sort(key=lambda x: x["puan"], reverse=True)
    return sonuclar[:limit]


def konu_detayi(konu: str) -> Optional[dict]:
    """Belirli bir konunun tüm detaylarını döner."""
    dosya = _konu_dosyasi_bul(konu)
    if not dosya:
        return None
    return _dosya_yukle(dosya)


def etiket_ara(konu: str, etiket_adi: str) -> Optional[dict]:
    """Belirli bir konudaki etiket/tag'ı arar."""
    veri = konu_detayi(konu)
    if not veri:
        return None

    etiket_lower = etiket_adi.lower()
    for etiket in veri.get("tags", []):
        if isinstance(etiket, dict):
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
