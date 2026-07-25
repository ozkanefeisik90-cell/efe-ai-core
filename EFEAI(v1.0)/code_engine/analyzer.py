"""
EFEAI Kod Analiz Motoru
Kullanıcının gönderdiği kodu analiz eder:
  - Sözdizimi kontrolü
  - Kalite değerlendirmesi
  - Güvenlik riskleri
  - İyileştirme önerileri
"""

import re
from typing import Optional


# ─── Dil Tespiti ──────────────────────────────────────────────

DILLER = {
    "python": {
        "belirtecler": [r'\bdef \w+\(', r'\bimport \w+', r'\bprint\(', r'\bif __name__',
                        r':\s*$', r'\bclass \w+[\(:]', r'\belif\b', r'\bNone\b', r'\bTrue\b', r'\bFalse\b'],
        "yorum": "#",
        "girintili": True,
    },
    "javascript": {
        "belirtecler": [r'\bfunction\b', r'\bconst\b', r'\blet\b', r'\bvar\b',
                        r'\bconsole\.log\b', r'=>', r'\bdocument\.', r'===', r'!=='],
        "yorum": "//",
        "girintili": False,
    },
    "java": {
        "belirtecler": [r'\bpublic\b', r'\bprivate\b', r'\bclass\b', r'\bSystem\.out\.',
                        r'\bstatic\b', r'\bvoid\b', r'\bnew\b', r'\bimport java\.'],
        "yorum": "//",
        "girintili": False,
    },
    "html": {
        "belirtecler": [r'<!DOCTYPE', r'<html', r'<head', r'<body', r'<div', r'<p>',
                        r'<h[1-6]', r'<a\s', r'<img\s', r'<form'],
        "yorum": "<!--",
        "girintili": False,
    },
    "css": {
        "belirtecler": [r'\{[^}]*\}', r':\s*\w+\s*;', r'^\s*\.\w+', r'^\s*#\w+',
                        r'@media', r'font-family', r'color:', r'background-color:'],
        "yorum": "/*",
        "girintili": False,
    },
    "sql": {
        "belirtecler": [r'\bSELECT\b', r'\bFROM\b', r'\bWHERE\b', r'\bINSERT\b',
                        r'\bUPDATE\b', r'\bDELETE\b', r'\bCREATE TABLE\b'],
        "yorum": "--",
        "girintili": False,
    },
    "dart": {
        "belirtecler": [r'\bvoid\b', r'\bWidget\b', r'\bFlutter\b', r'\bStateful\b',
                        r'\bStateless\b', r'\bbuildContext\b', r'import \'package:'],
        "yorum": "//",
        "girintili": False,
    },
}


def dil_tespit_et(kod: str) -> str:
    """Kodu analiz ederek kullanılan programlama dilini tahmin eder."""
    en_yuksek = 0
    tahmin = "bilinmiyor"

    for dil, bilgi in DILLER.items():
        puan = 0
        for belirtec in bilgi["belirtecler"]:
            if re.search(belirtec, kod, re.MULTILINE | re.IGNORECASE):
                puan += 1
        if puan > en_yuksek:
            en_yuksek = puan
            tahmin = dil

    return tahmin if en_yuksek > 0 else "bilinmiyor"


# ─── Python Analizi ───────────────────────────────────────────

def _python_analiz(kod: str) -> dict:
    satirlar = kod.splitlines()
    sorunlar = []
    oneriler = []
    puan = 100

    # Girinti kontrolü
    yanlis_girinti = False
    for i, satir in enumerate(satirlar, 1):
        if satir and not satir.startswith((' ', '\t', '#', 'def ', 'class ', 'import ',
                                            'from ', 'if ', 'for ', 'while ', 'try:',
                                            'except', 'else:', 'elif ', 'finally:',
                                            'return ', 'print(', 'with ', '@')):
            if '\t' in satir and '    ' in satir:
                sorunlar.append({
                    "seviye": "uyarı",
                    "satir": i,
                    "mesaj": "Karışık sekme ve boşluk girintisi tespit edildi.",
                    "cozum": "Sadece boşluk (4 adet) veya sadece sekme kullan; karıştırma."
                })
                puan -= 5
                yanlis_girinti = True

    # Boş except bloğu
    for i, satir in enumerate(satirlar, 1):
        if re.match(r'\s*except\s*:', satir):
            sorunlar.append({
                "seviye": "uyarı",
                "satir": i,
                "mesaj": "Genel 'except:' bloğu kullanılmış.",
                "cozum": "Spesifik exception türü belirt: except ValueError: veya except Exception as e:"
            })
            puan -= 8

    # print yerine logging önerisi (büyük projeler için)
    print_sayisi = len(re.findall(r'\bprint\(', kod))
    if print_sayisi > 5:
        oneriler.append("Büyük projelerde print() yerine logging modülü daha uygun olabilir.")

    # Çok uzun satırlar (PEP8: max 79 karakter)
    for i, satir in enumerate(satirlar, 1):
        if len(satir) > 100:
            sorunlar.append({
                "seviye": "bilgi",
                "satir": i,
                "mesaj": f"Satır çok uzun ({len(satir)} karakter). PEP8 standardı max 79 karakter önerir.",
                "cozum": "Satırı böl ya da değişkenleri ayrıştır."
            })
            puan -= 2

    # Kullanılmayan import tahmini (basit kontrol)
    importlar = re.findall(r'^\s*import (\w+)', kod, re.MULTILINE)
    from_importlar = re.findall(r'^\s*from \w+ import (\w+)', kod, re.MULTILINE)
    tum_importlar = importlar + from_importlar
    for imp in tum_importlar:
        # İmport edilen isim kodun geri kalanında geçiyor mu?
        import_siz = re.sub(r'^\s*(?:import|from)\s.*$', '', kod, flags=re.MULTILINE)
        if imp not in import_siz:
            oneriler.append(f"'{imp}' modülü import edilmiş ama kullanılmıyor olabilir.")

    # Magic number uyarısı
    sihirli_sayilar = re.findall(r'(?<!["\'\w])\b(?!0\b|1\b)[2-9]\d*\b', kod)
    if len(sihirli_sayilar) > 3:
        oneriler.append("Sihirli sayılar (2, 3, 42 gibi doğrudan sayılar) yerine sabit değişkenler kullan.")

    # Global değişken uyarısı
    if re.search(r'\bglobal\b', kod):
        oneriler.append("global anahtar kelimesi kullanımı dikkatli değerlendirilmeli; mümkünse fonksiyon parametresi kullan.")

    return {
        "sorunlar": sorunlar,
        "oneriler": oneriler,
        "puan": max(0, puan),
    }


# ─── HTML Analizi ─────────────────────────────────────────────

def _html_analiz(kod: str) -> dict:
    sorunlar = []
    oneriler = []
    puan = 100

    # DOCTYPE kontrolü
    if not re.search(r'<!DOCTYPE\s+html', kod, re.IGNORECASE):
        sorunlar.append({
            "seviye": "kritik",
            "satir": 1,
            "mesaj": "<!DOCTYPE html> bildirimi eksik.",
            "cozum": "Dosyanın ilk satırına <!DOCTYPE html> ekle."
        })
        puan -= 15

    # title kontrolü
    if not re.search(r'<title[^>]*>.*?</title>', kod, re.DOTALL | re.IGNORECASE):
        sorunlar.append({
            "seviye": "orta",
            "satir": None,
            "mesaj": "<title> etiketi bulunamadı.",
            "cozum": "<head> bölümüne <title>Sayfa Adı</title> ekle."
        })
        puan -= 10

    # meta charset kontrolü
    if not re.search(r'<meta\s[^>]*charset', kod, re.IGNORECASE):
        sorunlar.append({
            "seviye": "orta",
            "satir": None,
            "mesaj": "Karakter seti (charset) meta etiketi eksik.",
            "cozum": "<head> içine <meta charset=\"UTF-8\"> ekle."
        })
        puan -= 8

    # alt özniteliği eksik img kontrol
    img_leri = re.findall(r'<img[^>]*>', kod, re.IGNORECASE)
    for img in img_leri:
        if 'alt=' not in img.lower():
            sorunlar.append({
                "seviye": "uyarı",
                "satir": None,
                "mesaj": f"img etiketi alt özniteliği olmadan kullanılmış: {img[:60]}",
                "cozum": "Her <img> etiketine açıklayıcı bir alt=\"...\" özniteliği ekle."
            })
            puan -= 5

    # Boş href kontrolü
    bos_href = re.findall(r'href\s*=\s*["\']?\s*["\']?', kod)
    if bos_href:
        oneriler.append("Boş veya sadece '#' içeren href değerlerini gerçek URL'lerle doldur.")

    # Semantik etiket önerisi
    if re.search(r'<div', kod, re.IGNORECASE):
        if not re.search(r'<(header|nav|main|article|section|footer)', kod, re.IGNORECASE):
            oneriler.append("div yerine semantik etiketler (header, nav, main, article, section, footer) kullan.")

    # meta viewport
    if not re.search(r'<meta\s[^>]*viewport', kod, re.IGNORECASE):
        oneriler.append("Mobil uyum için <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"> ekle.")

    # inline style uyarısı
    inline_style_sayisi = len(re.findall(r'style\s*=\s*["\']', kod, re.IGNORECASE))
    if inline_style_sayisi > 3:
        oneriler.append("Çok sayıda inline style kullanılmış. Stilleri ayrı bir CSS dosyasına taşımayı değerlendir.")

    return {
        "sorunlar": sorunlar,
        "oneriler": oneriler,
        "puan": max(0, puan),
    }


# ─── JavaScript Analizi ───────────────────────────────────────

def _javascript_analiz(kod: str) -> dict:
    sorunlar = []
    oneriler = []
    puan = 100

    # var yerine let/const önerisi
    var_sayisi = len(re.findall(r'\bvar\b', kod))
    if var_sayisi > 0:
        oneriler.append(f"'var' yerine 'const' veya 'let' kullan. ({var_sayisi} 'var' kullanımı tespit edildi)")
        puan -= min(var_sayisi * 3, 15)

    # == yerine === önerisi
    esitlik_sayisi = len(re.findall(r'(?<!=)={2}(?!=)', kod))
    if esitlik_sayisi > 0:
        oneriler.append(f"'==' yerine '===' kullan (strict equality). ({esitlik_sayisi} kullanım)")
        puan -= min(esitlik_sayisi * 3, 10)

    # console.log üretim kodu uyarısı
    console_sayisi = len(re.findall(r'\bconsole\.log\b', kod))
    if console_sayisi > 3:
        oneriler.append(f"Üretim kodunda {console_sayisi} adet console.log var. Debug bitince kaldırmayı unutma.")

    # eval() güvenlik uyarısı
    if re.search(r'\beval\s*\(', kod):
        sorunlar.append({
            "seviye": "kritik",
            "satir": None,
            "mesaj": "eval() kullanımı tehlikeli olabilir (güvenlik açığı).",
            "cozum": "eval() yerine JSON.parse() veya Function() constructor kullan."
        })
        puan -= 20

    # innerHTML XSS uyarısı
    if re.search(r'innerHTML\s*=', kod):
        sorunlar.append({
            "seviye": "uyarı",
            "satir": None,
            "mesaj": "innerHTML kullanımı XSS saldırısına açık olabilir.",
            "cozum": "Kullanıcıdan gelen içerik için textContent kullan veya içeriği sanitize et."
        })
        puan -= 10

    return {
        "sorunlar": sorunlar,
        "oneriler": oneriler,
        "puan": max(0, puan),
    }


# ─── SQL Analizi ──────────────────────────────────────────────

def _sql_analiz(kod: str) -> dict:
    sorunlar = []
    oneriler = []
    puan = 100

    # SELECT * uyarısı
    if re.search(r'SELECT\s+\*', kod, re.IGNORECASE):
        oneriler.append("SELECT * yerine ihtiyaç duyulan sütunları açıkça belirt; performans için önemli.")

    # SQL Injection riski (string birleştirme)
    if re.search(r'["\'].*\+.*WHERE|WHERE.*\+.*["\']', kod, re.IGNORECASE):
        sorunlar.append({
            "seviye": "kritik",
            "satir": None,
            "mesaj": "Olası SQL Injection riski: string birleştirme ile sorgu oluşturulmuş.",
            "cozum": "Parameterized queries (prepared statements) kullan."
        })
        puan -= 25

    # DROP TABLE uyarısı
    if re.search(r'\bDROP\s+TABLE\b', kod, re.IGNORECASE):
        sorunlar.append({
            "seviye": "kritik",
            "satir": None,
            "mesaj": "DROP TABLE komutu tespit edildi. Dikkatli kullanılmalıdır.",
            "cozum": "Bu komutu çalıştırmadan önce yedek aldığından emin ol."
        })

    return {
        "sorunlar": sorunlar,
        "oneriler": oneriler,
        "puan": max(0, puan),
    }


# ─── Genel Metrikler ──────────────────────────────────────────

def _genel_metrikler(kod: str, dil: str) -> dict:
    satirlar = kod.splitlines()
    toplam_satir = len(satirlar)
    bos_satir = sum(1 for s in satirlar if not s.strip())
    yorum_satiri = 0

    yorum_ek = DILLER.get(dil, {}).get("yorum", "#")
    for satir in satirlar:
        temiz = satir.strip()
        if temiz.startswith(yorum_ek):
            yorum_satiri += 1

    kod_satiri = toplam_satir - bos_satir - yorum_satiri
    yorum_orani = (yorum_satiri / max(toplam_satir, 1)) * 100

    return {
        "toplam_satir": toplam_satir,
        "kod_satiri": kod_satiri,
        "bos_satir": bos_satir,
        "yorum_satiri": yorum_satiri,
        "yorum_orani": round(yorum_orani, 1),
    }


# ─── Ana Analiz Fonksiyonu ────────────────────────────────────

def kodu_analiz_et(kod: str, dil: Optional[str] = None) -> dict:
    """
    Verilen kodu analiz eder ve kapsamlı rapor döner.
    
    Returns:
        dict: {
            dil, metrikler, sorunlar, oneriler,
            guvenlik_riskleri, puan, ozet
        }
    """
    if not kod.strip():
        return {"hata": "Analiz edilecek kod boş."}

    tespit_edilen_dil = dil or dil_tespit_et(kod)
    metrikler = _genel_metrikler(kod, tespit_edilen_dil)

    # Dile özgü analiz
    dil_analizleri = {
        "python": _python_analiz,
        "javascript": _javascript_analiz,
        "html": _html_analiz,
        "sql": _sql_analiz,
    }

    if tespit_edilen_dil in dil_analizleri:
        dil_sonucu = dil_analizleri[tespit_edilen_dil](kod)
    else:
        dil_sonucu = {"sorunlar": [], "oneriler": [], "puan": 80}

    # Güvenlik risklerini ayır
    guvenlik_riskleri = [
        s for s in dil_sonucu["sorunlar"]
        if s.get("seviye") == "kritik"
    ]
    diger_sorunlar = [
        s for s in dil_sonucu["sorunlar"]
        if s.get("seviye") != "kritik"
    ]

    # Puan yorumu
    puan = dil_sonucu["puan"]
    if puan >= 90:
        puan_yorumu = "Çok İyi"
    elif puan >= 75:
        puan_yorumu = "İyi"
    elif puan >= 60:
        puan_yorumu = "Orta"
    elif puan >= 40:
        puan_yorumu = "Geliştirme Gerekli"
    else:
        puan_yorumu = "Kritik Sorunlar Var"

    return {
        "dil": tespit_edilen_dil,
        "metrikler": metrikler,
        "sorunlar": diger_sorunlar,
        "guvenlik_riskleri": guvenlik_riskleri,
        "oneriler": dil_sonucu["oneriler"],
        "puan": puan,
        "puan_yorumu": puan_yorumu,
    }


def analiz_raporu_formatla(analiz: dict) -> str:
    """Analiz sonucunu okunabilir metne çevirir."""
    if "hata" in analiz:
        return f"⚠ {analiz['hata']}"

    satirlar = []
    m = analiz.get("metrikler", {})

    satirlar.append("═══ KOD ANALİZ RAPORU ═══")
    satirlar.append(f"Dil          : {analiz.get('dil', '?').upper()}")
    satirlar.append(f"Toplam Satır : {m.get('toplam_satir', 0)}")
    satirlar.append(f"Kod Satırı   : {m.get('kod_satiri', 0)}")
    satirlar.append(f"Yorum Satırı : {m.get('yorum_satiri', 0)} (%{m.get('yorum_orani', 0)})")
    satirlar.append(f"Kalite Puanı : {analiz.get('puan', 0)}/100 — {analiz.get('puan_yorumu', '')}")

    grs = analiz.get("guvenlik_riskleri", [])
    if grs:
        satirlar.append(f"\n⛔ GÜVENLİK RİSKLERİ ({len(grs)}):")
        for r in grs:
            satirlar.append(f"  • {r['mesaj']}")
            satirlar.append(f"    → {r['cozum']}")

    sorunlar = analiz.get("sorunlar", [])
    if sorunlar:
        satirlar.append(f"\n⚠ SORUNLAR ({len(sorunlar)}):")
        for s in sorunlar:
            satir_bilgisi = f" (Satır {s['satir']})" if s.get("satir") else ""
            satirlar.append(f"  • [{s.get('seviye','?').upper()}]{satir_bilgisi} {s['mesaj']}")
            satirlar.append(f"    → {s['cozum']}")

    oneriler = analiz.get("oneriler", [])
    if oneriler:
        satirlar.append(f"\n💡 İYİLEŞTİRME ÖNERİLERİ ({len(oneriler)}):")
        for o in oneriler:
            satirlar.append(f"  • {o}")

    if not grs and not sorunlar and not oneriler:
        satirlar.append("\n✓ Dikkat çekici bir sorun bulunamadı.")

    return "\n".join(satirlar)
