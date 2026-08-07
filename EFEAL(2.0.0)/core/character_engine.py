"""
EFEAI Karakter Motoru
EFEAI'nin kişiliğini, konuşma tarzını ve yanıt biçimlendirmesini yönetir.
"""

import random
from typing import Optional


# ─── Konuşma Modu ─────────────────────────────────────────────
class ConversationMode:
    NORMAL = "normal"
    SAMIMI = "samimi"
    PROFESYONEL = "profesyonel"


# ─── Giriş Cümleleri (Duruma Göre) ───────────────────────────
OPENINGS_NORMAL = [
    "Şöyle açıklayayım.",
    "Bunu birlikte inceleyelim.",
    "İlginç bir nokta.",
    "Kısaca cevaplayayım.",
    "Bunu şöyle düşün.",
    "Şu şekilde anlatabilirim.",
    "İyi bir soru.",
    "Tam olarak.",
]

OPENINGS_SAMIMI = [
    "Dostum, şöyle anlayayım.",
    "Bak, bunu birlikte düşünelim.",
    "Dostum, güzel bir soru sordun.",
    "Harika bir nokta yakaladın.",
    "Bunu birlikte çözelim.",
    "Şöyle bir bakalım.",
]

OPENINGS_PROFESYONEL = [
    "Teknik açıdan değerlendirirsek:",
    "Bu konuda şunları söyleyebilirim:",
    "Standart yaklaşım şöyledir:",
    "Belirtmek gerekirse,",
    "Kesin olarak ifade etmek gerekirse:",
]

OPENINGS_TEBRIK = [
    "Harika iş çıkardın.",
    "Bunu güzel çözdün.",
    "Tam da doğru yapmışsın.",
    "Çok iyi bir yaklaşım.",
    "Bunu doğru anlamışsın.",
]

OPENINGS_HATA = [
    "Şurada küçük bir hata görüyorum.",
    "Bu kısmı şöyle değiştirirsen daha doğru çalışacaktır.",
    "Burada dikkat edilmesi gereken bir nokta var.",
    "Küçük bir düzeltme gerekiyor.",
    "Bu kısmı şöyle güncellersen daha iyi olur.",
]

MIZAH_EKLEMELERI = [
    "Bu hatayı çoğu geliştirici en az bir kez yapmıştır.",
    "Merak etme, bunu hepimiz yaşadık.",
    "Klasik bir tuzak, neredeyse bir gelenek haline geldi.",
]

BILMIYORUM_YANITLARI = [
    "Bu konuda bilgi tabanımda yeterli veri yok.",
    "Bu konuda sınırlı bilgim var, yanlış bilgi vermemek için belirtmek istedim.",
    "Bu konu bilgi tabanımın dışında kalıyor.",
    "Bu konuda kesin bir bilgim olmadığından cevap vermekten kaçınıyorum.",
]

OGRETICI_KAPANISLAR = [
    "Bu kodu kopyalayabilirsin ama neden çalıştığını da öğrenmeni tavsiye ederim.",
    "Kodu uygulamadan önce mantığını anlamaya çalış, daha kalıcı öğrenirsin.",
    "Bu yaklaşımı ezberlemek yerine neden böyle çalıştığını anlarsan farklı durumlarda da kullanabilirsin.",
    "Deneyerek öğrenmek en kalıcı yöntemdir.",
]

EFEAI_SOZLERI = [
    "Kod yalnızca çalışmamalı; anlaşılmalı da.",
    "Bilgi güçtür, anlaşılan bilgi ise ustalıktır.",
    "İyi kod, açıklamaya gerek duymayan değil; açıklaması anlamlı olan koddur.",
    "Her hata, yeni bir şey öğrenme fırsatıdır.",
    "Başlamak, mükemmel olmaktan önemlidir.",
]


class CharacterEngine:
    """
    EFEAI'nin konuşma kişiliğini ve yanıt biçimlendirmesini yönetir.
    """

    def __init__(self, mode: str = ConversationMode.NORMAL):
        self.mode = mode
        self._mesaj_sayaci = 0  # Hitap sıklığını kontrol etmek için

    def modu_degistir(self, yeni_mod: str):
        """Konuşma modunu değiştirir."""
        if yeni_mod in [ConversationMode.NORMAL, ConversationMode.SAMIMI, ConversationMode.PROFESYONEL]:
            self.mode = yeni_mod
            return True
        return False

    def acilis_cumle(self, tip: str = "normal") -> str:
        """
        Duruma göre açılış cümlesi seçer.
        tip: 'normal', 'samimi', 'profesyonel', 'tebrik', 'hata'
        """
        if tip == "tebrik":
            return random.choice(OPENINGS_TEBRIK)
        elif tip == "hata":
            return random.choice(OPENINGS_HATA)
        elif tip == "samimi" or self.mode == ConversationMode.SAMIMI:
            # Her mesajda samimi açılış kullanma, arada normal kullan
            self._mesaj_sayaci += 1
            if self._mesaj_sayaci % 3 == 0:  # Her 3 mesajda bir "dostum" vs.
                return random.choice(OPENINGS_SAMIMI)
            return random.choice(OPENINGS_NORMAL)
        elif tip == "profesyonel" or self.mode == ConversationMode.PROFESYONEL:
            return random.choice(OPENINGS_PROFESYONEL)
        else:
            return random.choice(OPENINGS_NORMAL)

    def bilmiyorum_yaniti(self) -> str:
        """Bilinmeyen konu için dürüst yanıt döner."""
        return random.choice(BILMIYORUM_YANITLARI)

    def ogretici_kapanisi(self) -> str:
        """Öğretici kapanış cümlesi döner."""
        return random.choice(OGRETICI_KAPANISLAR)

    def mizah_ekle(self, olasılık: float = 0.15) -> Optional[str]:
        """Belirli olasılıkla mizah ekler. Fazla kullanılmaz."""
        if random.random() < olasılık:
            return random.choice(MIZAH_EKLEMELERI)
        return None

    def efeai_sozu(self) -> str:
        """EFEAI'nin motto sözlerinden birini döner."""
        return random.choice(EFEAI_SOZLERI)

    def yanit_bicimlendirme(self, icerik: str, acilis: bool = True,
                             ogretici: bool = False, mizah: bool = False) -> str:
        """
        Verilen içeriği karakter motoruna göre biçimlendirir.
        """
        parcalar = []

        if acilis:
            parcalar.append(self.acilis_cumle())

        parcalar.append(icerik)

        if mizah:
            mizah_cumle = self.mizah_ekle()
            if mizah_cumle:
                parcalar.append(f"\n  [{mizah_cumle}]")

        if ogretici:
            parcalar.append(f"\n→ {self.ogretici_kapanisi()}")

        return "\n".join(p for p in parcalar if p)

    def hata_bildirimi(self, hata_detay: str) -> str:
        """Hata bulununca kullanıcıya nazikçe bildirir."""
        acilis = random.choice(OPENINGS_HATA)
        return f"{acilis}\n{hata_detay}"

    def selamlama(self) -> str:
        """İlk açılış selamlaması."""
        return "Merhaba! EFEAI hazır. Yazılım, kod veya teknoloji hakkında ne öğrenmek istiyorsun?"

    def veda(self) -> str:
        """Oturum kapanış mesajı."""
        soz = self.efeai_sozu()
        return f"Görüşmek üzere.\n\n\"{soz}\"\n— EFEAI"

    def mod_aciklamasi(self) -> str:
        """Mevcut modu açıklar."""
        modlar = {
            ConversationMode.NORMAL: "Normal — dengeli ve anlaşılır",
            ConversationMode.SAMIMI: "Samimi — daha sıcak ve arkadaşça",
            ConversationMode.PROFESYONEL: "Profesyonel — teknik ve resmi",
        }
        return modlar.get(self.mode, "Bilinmeyen mod")
