"""
EFEAI Güvenlik Tarayıcı
Koddaki güvenlik açıklarını ve riskli kalıpları tespit eder.
"""

import re
from typing import List


# ─── Güvenlik Kuralları ───────────────────────────────────────

GUVENLIK_KURALLARI = {
    "python": [
        {
            "id": "PY001",
            "kalip": r"eval\s*\(",
            "aciklama": "eval() kullanımı — keyfi kod çalıştırılabilir",
            "ciddiyet": "kritik",
            "cozum": "eval() yerine ast.literal_eval() kullan veya işlemi yeniden tasarla",
        },
        {
            "id": "PY002",
            "kalip": r"exec\s*\(",
            "aciklama": "exec() kullanımı — keyfi kod çalıştırılabilir",
            "ciddiyet": "kritik",
            "cozum": "exec() kullanımından kaçın; strateji deseni veya dictionary dispatch kullan",
        },
        {
            "id": "PY003",
            "kalip": r"os\.system\s*\(",
            "aciklama": "os.system() — shell injection riski",
            "ciddiyet": "yüksek",
            "cozum": "subprocess.run(args, shell=False) kullan ve argümanları liste olarak geç",
        },
        {
            "id": "PY004",
            "kalip": r"subprocess\..*shell\s*=\s*True",
            "aciklama": "subprocess ile shell=True — injection riski",
            "ciddiyet": "yüksek",
            "cozum": "shell=False kullan ve komut argümanlarını liste olarak geç",
        },
        {
            "id": "PY005",
            "kalip": r"pickle\.loads?\s*\(",
            "aciklama": "pickle.load() — güvenilmeyen veriyle kullanılırsa tehlikeli",
            "ciddiyet": "orta",
            "cozum": "Güvenilmeyen kaynaklardan gelen veriyi pickle ile işleme",
        },
        {
            "id": "PY006",
            "kalip": r"random\.\w+\s*\(",
            "aciklama": "random modülü — kriptografik güvenlik için uygun değil",
            "ciddiyet": "bilgi",
            "cozum": "Şifre, token üretimi için secrets modülünü kullan",
        },
        {
            "id": "PY007",
            "kalip": r'password\s*=\s*["\'][^"\']+["\']',
            "aciklama": "Hardcoded şifre tespit edildi",
            "ciddiyet": "kritik",
            "cozum": "Şifreyi kod içinde saklama; ortam değişkeni veya güvenli vault kullan",
        },
        {
            "id": "PY008",
            "kalip": r"(?:api_key|apikey|secret_key|token)\s*=\s*['\"][a-zA-Z0-9]{16,}['\"]",
            "aciklama": "Hardcoded API anahtarı veya secret tespit edildi",
            "ciddiyet": "kritik",
            "cozum": "API anahtarlarını .env dosyasına veya ortam değişkenine taşı",
        },
        {
            "id": "PY009",
            "kalip": r"debug\s*=\s*True",
            "aciklama": "Debug modu açık — production'da kapatılmalı",
            "ciddiyet": "orta",
            "cozum": "Production ortamında debug=False kullan",
        },
        {
            "id": "PY010",
            "kalip": r'sql\s*=.*["\'].*\+.*["\'].*WHERE',
            "aciklama": "String birleştirme ile SQL sorgusu — SQL injection riski",
            "ciddiyet": "kritik",
            "cozum": "Parametre bağlama kullan: cursor.execute(sql, (değer,))",
        },
    ],
    "javascript": [
        {
            "id": "JS001",
            "kalip": r"eval\s*\(",
            "aciklama": "eval() kullanımı — XSS ve keyfi kod riski",
            "ciddiyet": "kritik",
            "cozum": "eval() kullanımından kaçın; JSON.parse() veya Function() değerlendir",
        },
        {
            "id": "JS002",
            "kalip": r"\.innerHTML\s*=",
            "aciklama": "innerHTML ataması — XSS riski",
            "ciddiyet": "yüksek",
            "cozum": "Kullanıcı verisi için textContent kullan veya DOMPurify ile sanitize et",
        },
        {
            "id": "JS003",
            "kalip": r"document\.write\s*\(",
            "aciklama": "document.write() — XSS riski ve performans sorunu",
            "ciddiyet": "yüksek",
            "cozum": "DOM manipülasyonu için createElement / appendChild kullan",
        },
        {
            "id": "JS004",
            "kalip": r"(?:password|api_key|secret)\s*[:=]\s*['\"][a-zA-Z0-9]{8,}['\"]",
            "aciklama": "Hardcoded kimlik bilgisi",
            "ciddiyet": "kritik",
            "cozum": "Kimlik bilgilerini .env dosyasına veya environment değişkenine taşı",
        },
        {
            "id": "JS005",
            "kalip": r"localStorage\.setItem.*password",
            "aciklama": "Şifre localStorage'da saklanıyor",
            "ciddiyet": "yüksek",
            "cozum": "Şifreyi asla localStorage'da saklama; session veya güvenli cookie kullan",
        },
    ],
    "html": [
        {
            "id": "HTML001",
            "kalip": r"<script[^>]*src\s*=\s*[\"']http://",
            "aciklama": "HTTP üzerinden harici script — güvenli değil",
            "ciddiyet": "orta",
            "cozum": "HTTPS kullan ve Subresource Integrity (SRI) ekle",
        },
        {
            "id": "HTML002",
            "kalip": r"javascript:",
            "aciklama": "'javascript:' URL protokolü — XSS riski",
            "ciddiyet": "yüksek",
            "cozum": "Olay dinleyicisi kullan: addEventListener('click', handler)",
        },
        {
            "id": "HTML003",
            "kalip": r"<form(?![^>]*method=)",
            "aciklama": "Form methodu belirtilmemiş (varsayılan GET)",
            "ciddiyet": "bilgi",
            "cozum": "Hassas veri gönderirken method='POST' kullan",
        },
    ],
}

CIDDIYET_SIRASI = {"kritik": 4, "yüksek": 3, "orta": 2, "bilgi": 1}
CIDDIYET_IKONLARI = {
    "kritik": "🔴",
    "yüksek": "🟠",
    "orta":   "🟡",
    "bilgi":  "🔵",
}


class GuvenlikTarayici:
    """
    Kodu güvenlik açıkları açısından tarar.
    """

    def tara(self, kod: str, dil: str = None) -> str:
        """Kodda güvenlik taraması yapar."""
        if not dil:
            from code_engine.analyzer import dil_tespit_et
            dil = dil_tespit_et(kod)

        kurallar = GUVENLIK_KURALLARI.get(dil.lower(), [])

        if not kurallar:
            return f"'{dil}' dili için güvenlik kuralı tanımlı değil."

        bulgular = []
        for kural in kurallar:
            try:
                eslesme = re.search(kural["kalip"], kod, re.MULTILINE | re.IGNORECASE)
                if eslesme:
                    satir_no = self._satir_bul(kod, kural["kalip"])
                    bulgular.append({**kural, "satir": satir_no})
            except re.error:
                continue

        # Ciddiyete göre sırala
        bulgular.sort(
            key=lambda x: CIDDIYET_SIRASI.get(x["ciddiyet"], 0),
            reverse=True,
        )

        return self._rapor_formatla(bulgular, dil, len(kod.splitlines()))

    def _satir_bul(self, kod: str, kalip: str) -> int | None:
        """Kalıbın bulunduğu satır numarasını döner."""
        for i, satir in enumerate(kod.splitlines(), 1):
            try:
                if re.search(kalip, satir, re.IGNORECASE):
                    return i
            except re.error:
                pass
        return None

    def _rapor_formatla(self, bulgular: list, dil: str, satir_sayisi: int) -> str:
        """Güvenlik raporunu formatlar."""
        kritik = sum(1 for b in bulgular if b["ciddiyet"] == "kritik")
        yuksek = sum(1 for b in bulgular if b["ciddiyet"] == "yüksek")

        baslik = f"🔒 {dil.upper()} Güvenlik Tarama Raporu"
        ozet = f"   {satir_sayisi} satır tarandı • {len(bulgular)} bulgu"
        if kritik:
            ozet += f" • {kritik} KRİTİK"
        if yuksek:
            ozet += f" • {yuksek} YÜKSEK"

        if not bulgular:
            return f"{baslik}\n{ozet}\n\n✅ Bilinen güvenlik açığı tespit edilmedi."

        parcalar = [baslik, ozet, ""]
        for b in bulgular:
            ikon = CIDDIYET_IKONLARI.get(b["ciddiyet"], "•")
            satir_info = f" (Satır {b['satir']})" if b.get("satir") else ""
            parcalar.append(f"{ikon} [{b['id']}] {b['aciklama']}{satir_info}")
            parcalar.append(f"   Çözüm: {b['cozum']}")
            parcalar.append("")

        parcalar.append("─────────────────────────────────")
        parcalar.append("Not: Bu tarama statik analiz ile yapılmaktadır.")
        parcalar.append("Gerçek güvenlik testi için uzman desteği alınmalıdır.")
        return "\n".join(parcalar)

    def guvenli_kod_mu(self, kod: str, dil: str = "python") -> bool:
        """Kritik veya yüksek riskli bulgu yoksa True döner."""
        kurallar = GUVENLIK_KURALLARI.get(dil.lower(), [])
        for kural in kurallar:
            if kural["ciddiyet"] in ("kritik", "yüksek"):
                try:
                    if re.search(kural["kalip"], kod, re.MULTILINE | re.IGNORECASE):
                        return False
                except re.error:
                    pass
        return True
