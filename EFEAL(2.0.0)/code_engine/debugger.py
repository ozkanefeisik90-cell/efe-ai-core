"""
EFEAI Kod Hata Ayıklayıcı
Koddaki yaygın hataları tespit eder ve çözüm önerir.
"""

import re
from typing import Optional


YAYGIN_PYTHON_HATALARI = [
    {
        "kalip": r"print\s+['\"]",
        "sorun": "Python 2 sözdizimi: print ifadesi (parantez yok)",
        "cozum": "Python 3'te print fonksiyon: print('Merhaba')",
        "seviye": "hata",
    },
    {
        "kalip": r"==['\"]True['\"]|==['\"]False['\"]",
        "sorun": "Boolean değerler string olarak karşılaştırılmış",
        "cozum": "if durum == True yerine if durum: kullan",
        "seviye": "uyarı",
    },
    {
        "kalip": r"except\s*:",
        "sorun": "Genel 'except:' bloğu — tüm hataları yakalar",
        "cozum": "except Exception as e: veya spesifik exception türü kullan",
        "seviye": "uyarı",
    },
    {
        "kalip": r"l\s*=\s*\[\]\s*\n.*\.append",
        "sorun": "Liste oluşturup append kullanmak yerine list comprehension tercih et",
        "cozum": "sonuc = [islev(x) for x in liste]",
        "seviye": "bilgi",
    },
    {
        "kalip": r"import \*",
        "sorun": "Wildcard import — hangi isimlerin geleceği belirsiz",
        "cozum": "Sadece kullandıklarını import et: from modül import fonksiyon",
        "seviye": "uyarı",
    },
    {
        "kalip": r"def\s+\w+\([^)]*\)\s*:\s*\n\s*pass",
        "sorun": "Boş fonksiyon — pass ile doldurulmuş",
        "cozum": "Fonksiyonu uygulamayı unutmuş olabilirsin",
        "seviye": "bilgi",
    },
    {
        "kalip": r"== None",
        "sorun": "'== None' yerine 'is None' kullanılmalı",
        "cozum": "if degisken is None: kullan",
        "seviye": "uyarı",
    },
    {
        "kalip": r"!= None",
        "sorun": "'!= None' yerine 'is not None' kullanılmalı",
        "cozum": "if degisken is not None: kullan",
        "seviye": "uyarı",
    },
    {
        "kalip": r'open\([^)]+\)(?!\s*as)',
        "sorun": "Dosya 'with' bloğu olmadan açılmış",
        "cozum": "with open('dosya.txt') as f: kullan — otomatik kapatır",
        "seviye": "uyarı",
    },
    {
        "kalip": r"while True:",
        "sorun": "Sonsuz döngü — çıkış koşulu kontrol et",
        "cozum": "break ifadesi veya döngü koşulu eklemeyi unutma",
        "seviye": "bilgi",
    },
]

YAYGIN_JS_HATALARI = [
    {
        "kalip": r"var\s",
        "sorun": "'var' kullanımı — kapsam sorunlarına yol açabilir",
        "cozum": "const veya let kullan — daha güvenli kapsam",
        "seviye": "uyarı",
    },
    {
        "kalip": r"==(?!=)",
        "sorun": "Gevşek eşitlik (==) yerine katı eşitlik (===) kullan",
        "cozum": "=== operatörü tür dönüşümü yapmaz ve daha güvenlidir",
        "seviye": "uyarı",
    },
    {
        "kalip": r"\.innerHTML\s*=",
        "sorun": "innerHTML kullanımı XSS açığına yol açabilir",
        "cozum": "Kullanıcı verisi için textContent kullan veya sanitize et",
        "seviye": "güvenlik",
    },
    {
        "kalip": r"eval\(",
        "sorun": "eval() kullanımı güvenlik riski ve performans sorunu",
        "cozum": "eval() yerine JSON.parse() veya Function() kullan",
        "seviye": "güvenlik",
    },
    {
        "kalip": r"console\.log",
        "sorun": "console.log production kodunda kalmamalı",
        "cozum": "Production'da logları kaldır veya loglama kütüphanesi kullan",
        "seviye": "bilgi",
    },
]

YAYGIN_HTML_HATALARI = [
    {
        "kalip": r"<img(?![^>]*alt=)",
        "sorun": "img etiketinde alt özniteliği eksik",
        "cozum": "<img src='...' alt='Resim açıklaması'> — erişilebilirlik için zorunlu",
        "seviye": "uyarı",
    },
    {
        "kalip": r"<a(?![^>]*href=)",
        "sorun": "href özniteliği olmayan <a> etiketi",
        "cozum": "<a href='url'>Metin</a> şeklinde href ekle",
        "seviye": "hata",
    },
    {
        "kalip": r"<!DOCTYPE html>.*<html",
        "sorun": "DOCTYPE bildirimi eksik veya yanlış yerde",
        "cozum": "Dosyanın en başında <!DOCTYPE html> olmalı",
        "seviye": "hata",
    },
    {
        "kalip": r"<h[2-6]",
        "sorun": "Üst başlık (h1) olmadan alt başlık kullanılmış olabilir",
        "cozum": "Başlık hiyerarşisi h1 → h2 → h3 sırasıyla olmalı",
        "seviye": "bilgi",
    },
]

DİL_HATALARI = {
    "python": YAYGIN_PYTHON_HATALARI,
    "javascript": YAYGIN_JS_HATALARI,
    "html": YAYGIN_HTML_HATALARI,
}


class KodHataAyiklayici:
    """
    Koddaki yaygın hataları tespit eder ve çözüm önerir.
    """

    def hatalar_bul(self, kod: str, dil: str = "python") -> str:
        """Koddaki hataları bulur ve formatlanmış rapor döner."""
        hatalar = DİL_HATALARI.get(dil.lower(), [])
        bulunanlar = []

        for hata_tanimi in hatalar:
            kalip = hata_tanimi["kalip"]
            try:
                if re.search(kalip, kod, re.MULTILINE | re.IGNORECASE):
                    # Satır numarasını bul
                    satir_no = self._satir_bul(kod, kalip)
                    bulunanlar.append({
                        **hata_tanimi,
                        "satir": satir_no,
                    })
            except re.error:
                continue

        return self._rapor_formatla(bulunanlar, dil)

    def _satir_bul(self, kod: str, kalip: str) -> Optional[int]:
        """Kalıbın bulunduğu satır numarasını döner."""
        for i, satir in enumerate(kod.splitlines(), 1):
            try:
                if re.search(kalip, satir, re.IGNORECASE):
                    return i
            except re.error:
                pass
        return None

    def _rapor_formatla(self, hatalar: list, dil: str) -> str:
        """Hata raporunu formatlar."""
        if not hatalar:
            return f"✅ {dil.upper()} kodunda bilinen yaygın hata kalıbı bulunamadı."

        seviye_ikonlari = {
            "hata":     "❌",
            "uyarı":    "⚠️",
            "bilgi":    "ℹ️",
            "güvenlik": "🔒",
        }

        satirlar = [f"🔍 {dil.upper()} Kod Analizi — {len(hatalar)} bulgu:", ""]
        for h in hatalar:
            ikon = seviye_ikonlari.get(h["seviye"], "•")
            satir_bilgi = f" (Satır ~{h['satir']})" if h.get("satir") else ""
            satirlar.append(f"{ikon} {h['sorun']}{satir_bilgi}")
            satirlar.append(f"   → {h['cozum']}")
            satirlar.append("")

        return "\n".join(satirlar)

    def alternatif_yaklaşım(self, kod: str, dil: str) -> str:
        """Alternatif yaklaşım önerir."""
        return (
            f"Bu kodu yazmanın alternatif bir yolu:\n"
            f"Daha iyi pratikler için '{dil} best practices' konusunu inceleyebilirsin."
        )
