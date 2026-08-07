"""
EFEAI Hafıza Modülü
Konuşma geçmişi, bağlam takibi ve kısa-uzun vadeli hafıza yönetimi.
"""

from datetime import datetime
from typing import Optional
from database import db


class Memory:
    """
    EFEAI'nin oturum içi ve kalıcı hafızasını yönetir.
    Kısa vadeli: Mevcut oturumun mesajları (RAM).
    Uzun vadeli: SQLite veritabanına kaydedilen geçmiş.
    """

    def __init__(self, session_id: str, max_gecmis: int = 50):
        self.session_id = session_id
        self.max_gecmis = max_gecmis
        self._gecmis: list[dict] = []          # Kısa vadeli RAM hafızası
        self._son_konu: Optional[str] = None   # Son konuşulan konu
        self._son_intent: Optional[str] = None # Son tespit edilen niyet
        self._konu_sayaci: dict[str, int] = {} # Kaç kez hangi konu soruldu

    # ─── Kısa Vadeli Hafıza ───────────────────────────────────

    def ekle(self, rol: str, mesaj: str, konu: str = None, intent: str = None):
        """Oturum hafızasına mesaj ekler."""
        kayit = {
            "rol": rol,
            "mesaj": mesaj,
            "konu": konu,
            "intent": intent,
            "zaman": datetime.now().strftime("%H:%M:%S"),
        }
        self._gecmis.append(kayit)

        # Limit aşımında en eski mesajları sil
        if len(self._gecmis) > self.max_gecmis:
            self._gecmis = self._gecmis[-self.max_gecmis:]

        # Konu takibi
        if konu:
            self._son_konu = konu
            self._konu_sayaci[konu] = self._konu_sayaci.get(konu, 0) + 1

        if intent:
            self._son_intent = intent

    def son_mesajlar(self, adet: int = 10) -> list[dict]:
        """Son N mesajı döner."""
        return self._gecmis[-adet:]

    def son_kullanici_mesaji(self) -> Optional[str]:
        """Son kullanıcı mesajını döner."""
        for kayit in reversed(self._gecmis):
            if kayit["rol"] == "user":
                return kayit["mesaj"]
        return None

    def son_konu(self) -> Optional[str]:
        """Son konuşulan konuyu döner."""
        return self._son_konu

    def en_cok_sorulan_konular(self, limit: int = 5) -> list[tuple]:
        """En çok sorulan konuları döner."""
        sıralı = sorted(self._konu_sayaci.items(), key=lambda x: x[1], reverse=True)
        return sıralı[:limit]

    def oturum_ozeti(self) -> dict:
        """Mevcut oturumun özetini döner."""
        kullanici_mesaj = sum(1 for m in self._gecmis if m["rol"] == "user")
        efeai_mesaj = sum(1 for m in self._gecmis if m["rol"] == "efeai")
        konular = list(self._konu_sayaci.keys())

        return {
            "session_id": self.session_id,
            "toplam_mesaj": len(self._gecmis),
            "kullanici_mesaj": kullanici_mesaj,
            "efeai_mesaj": efeai_mesaj,
            "konular": konular,
            "son_konu": self._son_konu,
        }

    def temizle(self):
        """Oturum hafızasını temizler (yeni konuşma)."""
        self._gecmis.clear()
        self._son_konu = None
        self._son_intent = None
        self._konu_sayaci.clear()

    # ─── Uzun Vadeli Hafıza (DB) ──────────────────────────────

    def kalici_kaydet(self, rol: str, mesaj: str, konu: str = None, mod: str = "normal"):
        """Mesajı kalıcı olarak veritabanına kaydeder."""
        db.konusma_kaydet(self.session_id, rol, mesaj, topic=konu, mode=mod)

    def gecmis_oturumlar(self, limit: int = 5) -> list[dict]:
        """Geçmiş oturumları döner."""
        return db.konusma_gecmisi(limit=limit)

    def gecmis_konular(self) -> list[str]:
        """Daha önce konuşulan tüm konuları döner."""
        gecmis = db.konusma_gecmisi(limit=500)
        konular = set()
        for kayit in gecmis:
            if kayit.get("topic"):
                konular.add(kayit["topic"])
        return sorted(konular)

    # ─── Bağlam Takibi ────────────────────────────────────────

    def baglam_konu(self) -> Optional[str]:
        """
        Son 3 mesajdan bağlam konusunu çıkarır.
        Kullanıcı aynı konuya devam ediyorsa o konuyu döner.
        """
        son = self.son_mesajlar(6)
        konu_listesi = [m.get("konu") for m in son if m.get("konu")]
        if not konu_listesi:
            return None
        # En son tekrar eden konu
        from collections import Counter
        sayac = Counter(konu_listesi)
        return sayac.most_common(1)[0][0]

    def devam_mi(self, yeni_konu: str) -> bool:
        """Yeni konu, son konuşulan konuyla ilgili mi?"""
        son = self.baglam_konu()
        if not son or not yeni_konu:
            return False
        return son.lower() in yeni_konu.lower() or yeni_konu.lower() in son.lower()
