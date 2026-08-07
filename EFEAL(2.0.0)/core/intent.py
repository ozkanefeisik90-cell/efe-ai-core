"""
EFEAI Niyet Tanıma Modülü
Kullanıcı girdisinden ne istenildiğini tespit eder.
Kural tabanlı + anahtar kelime eşleştirme sistemi.
"""

import re
from typing import Optional


# ─── Niyet Sabitleri ──────────────────────────────────────────

class Intent:
    SELAMLAMA      = "selamlama"
    VEDA           = "veda"
    BILGI_ARA      = "bilgi_ara"
    ETIKET_ARA     = "etiket_ara"
    ORNEK_ISTE     = "ornek_iste"
    HATA_ARA       = "hata_ara"
    IPUCU_ISTE     = "ipucu_iste"
    KOD_ANALIZ     = "kod_analiz"
    KOD_YAZ        = "kod_yaz"
    KONU_LISTESI   = "konu_listesi"
    MOD_DEGISTIR   = "mod_degistir"
    ISTATISTIK     = "istatistik"
    YARDIM         = "yardim"
    PROJE          = "proje"
    NOT_ISLE       = "not_isle"
    QUIZ           = "quiz"
    YOL_HARITASI   = "yol_haritasi"
    GENEL_ARAMA    = "genel_arama"
    TANIMLA        = "tanimla"
    KARSILASTIR    = "karsilastir"
    OZETLE         = "ozetle"


# ─── Niyet Kalıpları ──────────────────────────────────────────

NIYET_KALIPLARI = {
    Intent.SELAMLAMA: [
        "merhaba", "selam", "hey", "hello", "hi", "günaydın", "iyi günler",
        "nasılsın", "naber", "ne haber",
    ],
    Intent.VEDA: [
        "görüşürüz", "güle güle", "bye", "çıkış", "exit", "quit", "hoşça kal",
        "kapatıyorum", "kapan", "kapat",
    ],
    Intent.KOD_ANALIZ: [
        "analiz et", "kodu incele", "kodu analiz", "kodu kontrol", "analyze",
        "hataları bul", "kod hatası", "bu kod", "kodumu kontrol", "incele",
    ],
    Intent.KOD_YAZ: [
        "kod yaz", "yaz bana", "oluştur", "üret", "generate", "create",
        "fonksiyon yaz", "class yaz", "script yaz",
    ],
    Intent.ETIKET_ARA: [
        "etiketi", "<", "tag nedir", "etiketten", "html etiketi",
    ],
    Intent.ORNEK_ISTE: [
        "örnek", "örnek ver", "örnek göster", "template", "şablon",
        "nasıl kullanılır", "kullanım örneği",
    ],
    Intent.HATA_ARA: [
        "hata", "error", "exception", "sorun", "problem",
        "neden çalışmıyor", "düzelt", "fix", "çalışmıyor",
    ],
    Intent.IPUCU_ISTE: [
        "ipucu", "tavsiye", "öneri", "tip", "dikkat", "püf noktası",
    ],
    Intent.BILGI_ARA: [
        "nedir", "ne demek", "anlat", "açıkla", "öğret", "öğrenmek istiyorum",
        "nasıl", "ne için", "ne işe yarar", "neden kullanılır",
    ],
    Intent.TANIMLA: [
        "tanımla", "tanım ver", "definition", "define",
    ],
    Intent.KARSILASTIR: [
        "farkı nedir", "karşılaştır", "hangisi daha iyi", "arasındaki fark",
        "compare", "vs", "karşısında",
    ],
    Intent.OZETLE: [
        "özetle", "kısaca anlat", "kısa anlat", "özet ver", "tldr",
    ],
    Intent.KONU_LISTESI: [
        "konular", "neler var", "liste", "ne öğrenebilirim", "kategoriler",
        "hangi konular", "ne var",
    ],
    Intent.MOD_DEGISTIR: [
        "mod değiştir", "samimi", "profesyonel", "normal mod",
        "konuşma modu", "modu değiştir", "modu değiştir",
    ],
    Intent.ISTATISTIK: [
        "istatistik", "durum", "kaç", "ne kadar", "rapor", "ilerleme",
    ],
    Intent.YARDIM: [
        "yardım", "help", "komutlar", "ne yapabilirsin", "özellikler",
    ],
    Intent.PROJE: [
        "proje", "workspace", "klasör yapısı", "proje oluştur",
    ],
    Intent.NOT_ISLE: [
        "not al", "not ekle", "not kaydet", "notlarım",
    ],
    Intent.QUIZ: [
        "quiz", "sınav", "test et", "soruları sor", "ne kadar biliyorum",
    ],
    Intent.YOL_HARITASI: [
        "yol haritası", "roadmap", "nereden başlamalıyım", "öğrenme yolu",
        "sıra", "nereden başlayım",
    ],
}


# ─── Niyet Dedektörü ──────────────────────────────────────────

class IntentDetector:
    """
    Kullanıcı girdisinden niyet tespit eder.
    Öncelikli kalıplara göre sıralı kontrol yapar.
    """

    # Öncelik sırası — daha özel olanlar önce
    ONCELIK = [
        Intent.VEDA, Intent.SELAMLAMA,
        Intent.KOD_ANALIZ, Intent.KOD_YAZ,
        Intent.ETIKET_ARA, Intent.ORNEK_ISTE,
        Intent.HATA_ARA, Intent.IPUCU_ISTE,
        Intent.KARSILASTIR, Intent.OZETLE, Intent.TANIMLA,
        Intent.BILGI_ARA,
        Intent.KONU_LISTESI, Intent.MOD_DEGISTIR,
        Intent.ISTATISTIK, Intent.YARDIM,
        Intent.PROJE, Intent.NOT_ISLE,
        Intent.QUIZ, Intent.YOL_HARITASI,
        Intent.GENEL_ARAMA,
    ]

    def tespit_et(self, girdi: str) -> dict:
        """
        Girdi metninden niyeti tespit eder.
        Returns: {"intent": str, "guven": float, "ozgul": bool}
        """
        g = girdi.lower().strip()

        # Kod bloğu içeriyorsa doğrudan analiz
        if self._kod_blogu_var_mi(girdi):
            return {"intent": Intent.KOD_ANALIZ, "guven": 0.95, "ozgul": True}

        # Kalıp eşleştirme
        en_iyi = None
        en_yuksek_puan = 0

        for niyet in self.ONCELIK[:-1]:  # GENEL_ARAMA hariç
            kaliplar = NIYET_KALIPLARI.get(niyet, [])
            puan = self._puan_hesapla(g, kaliplar)
            if puan > en_yuksek_puan:
                en_yuksek_puan = puan
                en_iyi = niyet

        if en_iyi and en_yuksek_puan > 0:
            return {
                "intent": en_iyi,
                "guven": min(1.0, en_yuksek_puan / 3.0),
                "ozgul": en_yuksek_puan >= 2,
            }

        return {"intent": Intent.GENEL_ARAMA, "guven": 0.3, "ozgul": False}

    def _puan_hesapla(self, metin: str, kaliplar: list) -> float:
        """Metin-kalıp eşleşme puanı hesaplar."""
        puan = 0.0
        for kalip in kaliplar:
            if kalip in metin:
                # Tam kelime eşleşmesi daha yüksek puan
                if re.search(r'\b' + re.escape(kalip) + r'\b', metin):
                    puan += 1.5
                else:
                    puan += 1.0
        return puan

    def _kod_blogu_var_mi(self, girdi: str) -> bool:
        """Girdi kod bloğu içeriyor mu?"""
        if "```" in girdi:
            return True
        satirlar = girdi.splitlines()
        if len(satirlar) >= 3:
            kod_sayisi = sum(
                1 for s in satirlar
                if re.search(r'(def |class |import |<html|<div|SELECT |function |const |var |let )', s)
            )
            return kod_sayisi >= 2
        return False

    def konu_cikar(self, girdi: str, intent: str) -> Optional[str]:
        """
        Girdiden konu adını çıkarır.
        Örn: "Python nedir" → "Python"
        """
        g = girdi.strip()

        # Teknoloji adları
        teknolojiler = [
            "Python", "JavaScript", "Java", "HTML", "CSS", "SQL",
            "Git", "Linux", "Flutter", "Dart", "React", "Node",
            "TypeScript", "C++", "C#", "PHP", "Ruby", "Go", "Rust",
            "Django", "Flask", "FastAPI", "Express",
        ]
        for tek in teknolojiler:
            if tek.lower() in g.lower():
                return tek

        # "X nedir" kalıbı
        m = re.search(r'(\w+)\s+nedir', g, re.IGNORECASE)
        if m:
            return m.group(1)

        # "X anlat" kalıbı
        m = re.search(r'(\w+)\s+anlat', g, re.IGNORECASE)
        if m:
            return m.group(1)

        # "X açıkla" kalıbı
        m = re.search(r'(\w+)\s+açıkla', g, re.IGNORECASE)
        if m:
            return m.group(1)

        return None


# Tekil örnek
_detector = IntentDetector()


def intent_tespit_et(girdi: str) -> dict:
    """Modül düzeyinde niyet tespit fonksiyonu."""
    return _detector.tespit_et(girdi)


def konu_cikar(girdi: str, intent: str = None) -> Optional[str]:
    """Modül düzeyinde konu çıkarma fonksiyonu."""
    return _detector.konu_cikar(girdi, intent or "")
