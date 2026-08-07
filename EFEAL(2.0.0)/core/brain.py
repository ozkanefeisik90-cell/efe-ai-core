"""
EFEAI Beyin Motoru
Kullanıcı sorgularını analiz eder, doğru modüle yönlendirir ve yanıt üretir.
"""

import re
import textwrap
from typing import Optional

from core.character_engine import CharacterEngine, ConversationMode
from core.settings import SettingsManager
from knowledge_base import searcher
from code_engine.analyzer import kodu_analiz_et, analiz_raporu_formatla
from database import db


class Brain:
    """
    EFEAI'nin merkezi karar ve yanıt üretim motoru.
    """

    def __init__(self):
        self.ayarlar = SettingsManager()
        mod = self.ayarlar.al("conversation_mode", "normal")
        self.karakter = CharacterEngine(mode=mod)
        self.session_id = self._session_id_olustur()
        self._mesaj_sayisi = 0

    def _session_id_olustur(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("session_%Y%m%d_%H%M%S")

    # ─── Intent Tespiti ───────────────────────────────────────

    def _intent_tespit(self, girdi: str) -> dict:
        """Kullanıcı girdisinin niyetini tespit eder."""
        g = girdi.lower().strip()

        # ─ Kod analizi
        if any(k in g for k in ["analiz et", "kodu incele", "kodu analiz", "kodu kontrol",
                                  "analyze", "hataları bul", "kod hatası", "bu kod"]):
            return {"intent": "kod_analiz", "ozgul": True}

        # ─ Bilgi arama
        if any(k in g for k in ["nedir", "ne demek", "anlat", "açıkla", "öğret",
                                  "nasıl", "ne için", "ne işe yarar"]):
            return {"intent": "bilgi_ara", "ozgul": False}

        # ─ Etiket/tag sorgulama
        if any(k in g for k in ["etiketi", "<", "tag", "etiketten"]):
            return {"intent": "etiket_ara", "ozgul": True}

        # ─ Örnek kod isteme
        if any(k in g for k in ["örnek", "örnek ver", "örnek göster", "kod ver",
                                  "kod yaz", "template", "şablon"]):
            return {"intent": "ornek_iste", "ozgul": True}

        # ─ Hata sorgulama
        if any(k in g for k in ["hata", "error", "exception", "sorun", "problem",
                                  "neden çalışmıyor", "düzelt", "fix"]):
            return {"intent": "hata_ara", "ozgul": False}

        # ─ İpucu isteme
        if any(k in g for k in ["ipucu", "tavsiye", "öneri", "tip", "dikkat"]):
            return {"intent": "ipucu_iste", "ozgul": True}

        # ─ Konu listesi
        if any(k in g for k in ["konular", "neler var", "liste", "ne öğrenebilirim",
                                  "kategoriler", "hangi konular"]):
            return {"intent": "konu_listesi", "ozgul": False}

        # ─ Proje işlemleri
        if any(k in g for k in ["proje", "workspace", "klasör yapısı"]):
            return {"intent": "proje", "ozgul": True}

        # ─ Mod değişikliği
        if any(k in g for k in ["mod değiştir", "samimi", "profesyonel", "normal mod",
                                  "konuşma modu", "modu değiştir"]):
            return {"intent": "mod_degistir", "ozgul": True}

        # ─ İstatistikler
        if any(k in g for k in ["istatistik", "durum", "kaç", "ne kadar", "rapor"]):
            return {"intent": "istatistik", "ozgul": False}

        # ─ Yardım
        if any(k in g for k in ["yardım", "help", "komutlar", "ne yapabilirsin"]):
            return {"intent": "yardim", "ozgul": False}

        # ─ Selamlama
        if any(k in g for k in ["merhaba", "selam", "hey", "hello", "hi"]):
            return {"intent": "selamlama", "ozgul": False}

        # ─ Veda
        if any(k in g for k in ["görüşürüz", "güle güle", "bye", "çıkış", "exit", "quit"]):
            return {"intent": "veda", "ozgul": False}

        # Varsayılan: genel arama
        return {"intent": "genel_arama", "ozgul": False}

    # ─── Konu Çıkarma ─────────────────────────────────────────

    def _konu_cikar(self, girdi: str) -> Optional[str]:
        """Kullanıcı girdisinden teknoloji konusunu çıkarır."""
        g = girdi.lower()
        bilinen_konular = ["html", "css", "javascript", "python", "java",
                           "flutter", "dart", "sql", "git", "linux",
                           "typescript", "react", "api", "json"]
        for k in bilinen_konular:
            if k in g:
                return k.upper() if k in ("html", "css", "sql") else k.capitalize()
        return None

    def _etiket_cikar(self, girdi: str) -> Optional[str]:
        """Girdi içinden HTML tag adını çıkarır."""
        eslesmeler = re.findall(r'<(\w+)', girdi)
        if eslesmeler:
            return eslesmeler[0]
        # "<h1 etiketi>" gibi ifadeler
        eslesmeler = re.findall(r'\b(h[1-6]|p|div|span|a|img|ul|ol|li|form|input|button|'
                                r'nav|header|footer|main|section|article|table|tr|td|th|'
                                r'textarea|select|label|code|pre|br|hr|script|style|link|meta|title)\b',
                                girdi.lower())
        if eslesmeler:
            return eslesmeler[0]
        return None

    # ─── Yanıt Üretimi ────────────────────────────────────────

    def _yanit_bilgi_ara(self, girdi: str) -> str:
        """Bilgi tabanında genel arama yapar."""
        sonuclar = searcher.genel_arama(girdi, limit=3)

        if not sonuclar:
            return self.karakter.bilmiyorum_yaniti()

        parcalar = []
        for s in sonuclar[:2]:
            konu_adi = s.get("konu", s.get("dosya", "?"))
            tanim = s.get("ilgili_tanim", "")
            if tanim:
                parcalar.append(
                    f"▸ {konu_adi}\n"
                    + textwrap.fill(tanim, width=70, initial_indent="  ")
                )
            else:
                parcalar.append(f"▸ {konu_adi}")

        gövde = "\n\n".join(parcalar)

        # İlgili konular ekle
        konu = self._konu_cikar(girdi)
        if konu:
            ilgili = searcher.ilgili_konular(konu)
            if ilgili:
                gövde += f"\n\n→ İlgili konular: {', '.join(ilgili)}"

        return self.karakter.yanit_bicimlendirme(
            gövde, acilis=True,
            ogretici=self.ayarlar.al("teach_mode", True)
        )

    def _yanit_etiket_ara(self, girdi: str) -> str:
        """Belirli bir HTML/CSS etiketini açıklar."""
        etiket = self._etiket_cikar(girdi)
        konu = self._konu_cikar(girdi) or "HTML"

        if not etiket:
            return self._yanit_bilgi_ara(girdi)

        sonuc = searcher.etiket_ara(konu, etiket)
        if not sonuc:
            # Genel arama ile dene
            return self._yanit_bilgi_ara(girdi)

        satirlar = [
            f"<{sonuc['name']}> — {sonuc.get('category', '')}",
            "",
            textwrap.fill(sonuc.get("description", ""), width=70),
        ]

        if sonuc.get("example"):
            satirlar.append(f"\nKullanım:\n{sonuc['example']}")

        if sonuc.get("self_closing"):
            satirlar.append("\n(Bu etiket kendiliğinden kapanır, </...> gerekmez.)")

        gövde = "\n".join(satirlar)
        return self.karakter.yanit_bicimlendirme(gövde, acilis=True)

    def _yanit_ornek_iste(self, girdi: str) -> str:
        """Kod örneği döner."""
        konu = self._konu_cikar(girdi)
        if not konu:
            return self.karakter.bilmiyorum_yaniti()

        ornekler = searcher.ornek_al(konu)
        if not ornekler:
            return self._yanit_bilgi_ara(girdi)

        ornek = ornekler[0]
        satirlar = [
            f"▸ {ornek.get('title', 'Örnek')}",
            f"  {ornek.get('description', '')}",
            "",
            "─── KOD ───",
            ornek.get("code", ""),
            "───────────",
        ]

        if len(ornekler) > 1:
            diger_basliklar = [o.get("title", "?") for o in ornekler[1:3]]
            satirlar.append(f"\nDiğer örnekler: {', '.join(diger_basliklar)}")
            satirlar.append("Görmek için: ornek [başlık]")

        gövde = "\n".join(satirlar)
        return self.karakter.yanit_bicimlendirme(
            gövde, acilis=True,
            ogretici=self.ayarlar.al("teach_mode", True)
        )

    def _yanit_hata_ara(self, girdi: str) -> str:
        """Hata tablosunda arama yapar."""
        konu = self._konu_cikar(girdi) or "HTML"
        hatalar = searcher.hata_ara(konu, girdi)

        if not hatalar:
            return self._yanit_bilgi_ara(girdi)

        hata = hatalar[0]
        satirlar = [
            f"Sorun: {hata.get('problem', '')}",
            "",
            f"Çözüm: {textwrap.fill(hata.get('solution', ''), width=70)}",
        ]

        if hata.get("wrong_example"):
            satirlar.append(f"\nYanlış kullanım:\n{hata['wrong_example']}")

        if hata.get("correct_example"):
            satirlar.append(f"\nDoğru kullanım:\n{hata['correct_example']}")

        gövde = "\n".join(s for s in satirlar if s is not None)
        return self.karakter.hata_bildirimi(gövde)

    def _yanit_ipucu_iste(self, girdi: str) -> str:
        """Bilgi tabanından ipuçları döner."""
        konu = self._konu_cikar(girdi)
        if not konu:
            return self._yanit_bilgi_ara(girdi)

        ipuclari = searcher.ipuclari_al(konu)
        if not ipuclari:
            return self.karakter.bilmiyorum_yaniti()

        import random
        secilen = random.sample(ipuclari, min(5, len(ipuclari)))
        gövde = f"{konu} için ipuçları:\n" + "\n".join(f"  • {ip}" for ip in secilen)
        return self.karakter.yanit_bicimlendirme(gövde, acilis=True)

    def _yanit_konu_listesi(self) -> str:
        """Mevcut tüm konuları listeler."""
        konular = searcher.mevcut_konular()
        if not konular:
            return "Bilgi tabanı henüz boş."

        satirlar = ["Bilgi tabanındaki konular:\n"]
        for k in konular:
            satirlar.append(
                f"  • {k['konu']:<20} [{k['zorluk']:<10}] "
                f"{k['tanim_sayisi']} tanım, {k['etiket_sayisi']} etiket"
            )
        satirlar.append(
            "\nBir konu hakkında bilgi almak için: '<konu> nedir?' yaz"
        )
        return "\n".join(satirlar)

    def _yanit_mod_degistir(self, girdi: str) -> str:
        """Konuşma modunu değiştirir."""
        g = girdi.lower()
        if "samimi" in g:
            self.karakter.modu_degistir(ConversationMode.SAMIMI)
            self.ayarlar.guncelle("conversation_mode", "samimi")
            return "Samimi mod aktif. Daha arkadaşça konuşacağım."
        elif "profesyonel" in g:
            self.karakter.modu_degistir(ConversationMode.PROFESYONEL)
            self.ayarlar.guncelle("conversation_mode", "profesyonel")
            return "Profesyonel mod aktif. Teknik ve resmi bir üslupla devam edeceğim."
        else:
            self.karakter.modu_degistir(ConversationMode.NORMAL)
            self.ayarlar.guncelle("conversation_mode", "normal")
            return "Normal mod aktif."

    def _yanit_istatistik(self) -> str:
        """Genel istatistikleri döner."""
        stats = db.genel_istatistikler()
        satirlar = [
            "═══ EFEAI İSTATİSTİKLERİ ═══",
            f"  Projeler        : {stats['proje_sayisi']} (Tamamlanan: {stats['tamamlanan_proje']})",
            f"  Notlar          : {stats['not_sayisi']}",
            f"  Çalışılan Konu  : {stats['calisilan_konu']} (Tamamlanan: {stats['tamamlanan_konu']})",
            f"  Favoriler       : {stats['favori_sayisi']}",
            f"  Çalışma Süresi  : {stats['toplam_calisma_dk']} dakika",
            f"  Toplam Mesaj    : {stats['toplam_mesaj']}",
            f"\n  Konuşma Modu   : {self.karakter.mod_aciklamasi()}",
            f"  Oturum ID       : {self.session_id}",
        ]
        return "\n".join(satirlar)

    def _yanit_yardim(self) -> str:
        """Komut listesi ve kullanım kılavuzu."""
        return """═══ EFEAI — KULLANIM KILAVUZU ═══

▸ BİLGİ SORGULAMA
  html nedir              → Konu açıklaması
  <p> etiketi             → Belirli etiket bilgisi
  örnek göster            → Kod örneği

▸ KOD ANALİZİ
  [kodu buraya yapıştır]
  analiz et               → Kodu analiz eder

▸ HATA ÇÖZME
  hata bul / hata düzelt  → Yaygın hatalar ve çözümler
  ipuçları                → Konu ipuçları

▸ KONU LİSTESİ
  konular                 → Tüm konuları listeler

▸ PROJE YÖNETİMİ
  projeler                → Proje listesi

▸ AYARLAR
  mod: samimi             → Samimi konuşma modu
  mod: profesyonel        → Profesyonel konuşma modu
  mod: normal             → Normal konuşma modu

▸ DİĞER
  istatistikler           → Genel durum raporu
  yardım                  → Bu menüyü gösterir
  çıkış                   → Oturumu kapatır

─────────────────────────────
"Kod yalnızca çalışmamalı; anlaşılmalı da." — EFEAI"""

    # ─── Ana Yanıt Metodu ─────────────────────────────────────

    def yanit_uret(self, girdi: str) -> str:
        """
        Kullanıcı girdisini alır, işler ve yanıt döner.
        Aynı zamanda konuşmayı SQLite'a kaydeder.
        """
        girdi = girdi.strip()
        if not girdi:
            return ""

        self._mesaj_sayisi += 1

        # Konuşmayı kaydet (kullanıcı mesajı)
        db.konusma_kaydet(
            self.session_id, "user", girdi,
            topic=self._konu_cikar(girdi),
            mode=self.karakter.mode
        )

        # ─ Özel komutlar önce kontrol edilir
        girdi_lower = girdi.lower()

        # Mod değiştirme
        if "mod:" in girdi_lower or "modu:" in girdi_lower:
            yanit = self._yanit_mod_degistir(girdi_lower)
            self._konusmayi_kaydet_efeai(yanit, girdi)
            return yanit

        # Intent tespiti
        intent = self._intent_tespit(girdi)

        # Kod bloğu mu içeriyor? (analiz için)
        kod_blogu = self._kod_blogu_cikar(girdi)
        if kod_blogu:
            analiz = kodu_analiz_et(kod_blogu)
            yanit = analiz_raporu_formatla(analiz)
            if self.ayarlar.al("teach_mode", True):
                yanit += f"\n\n→ {self.karakter.ogretici_kapanisi()}"
            self._konusmayi_kaydet_efeai(yanit, girdi)
            return yanit

        # Intent'e göre yanıt üret
        if intent["intent"] == "selamlama":
            yanit = self.karakter.selamlama()
        elif intent["intent"] == "veda":
            yanit = self.karakter.veda()
        elif intent["intent"] == "yardim":
            yanit = self._yanit_yardim()
        elif intent["intent"] == "konu_listesi":
            yanit = self._yanit_konu_listesi()
        elif intent["intent"] == "istatistik":
            yanit = self._yanit_istatistik()
        elif intent["intent"] == "mod_degistir":
            yanit = self._yanit_mod_degistir(girdi)
        elif intent["intent"] == "etiket_ara":
            yanit = self._yanit_etiket_ara(girdi)
        elif intent["intent"] == "ornek_iste":
            yanit = self._yanit_ornek_iste(girdi)
        elif intent["intent"] == "hata_ara":
            yanit = self._yanit_hata_ara(girdi)
        elif intent["intent"] == "ipucu_iste":
            yanit = self._yanit_ipucu_iste(girdi)
        else:
            # Genel bilgi arama (hem bilgi_ara hem genel_arama için)
            yanit = self._yanit_bilgi_ara(girdi)

        # Boş yanıt güvenliği
        if not yanit or not yanit.strip():
            yanit = self.karakter.bilmiyorum_yaniti()

        self._konusmayi_kaydet_efeai(yanit, girdi)
        return yanit

    def _konusmayi_kaydet_efeai(self, yanit: str, orjinal_girdi: str):
        """EFEAI yanıtını veritabanına kaydeder."""
        db.konusma_kaydet(
            self.session_id, "efeai", yanit,
            topic=self._konu_cikar(orjinal_girdi),
            mode=self.karakter.mode
        )

    def _kod_blogu_cikar(self, girdi: str) -> Optional[str]:
        """
        Kullanıcı girdisinden kod bloğu çıkarır.
        ``` ile çevrilmiş veya çok satırlı girintili kod blokları.
        """
        # ```...``` bloğu
        eslesme = re.search(r'```(?:\w+)?\n?(.*?)```', girdi, re.DOTALL)
        if eslesme:
            return eslesme.group(1).strip()

        # Çok satırlı metin — en az 3 satır, en az biri < veya def/class/function içeriyorsa
        satirlar = girdi.splitlines()
        if len(satirlar) >= 3:
            kod_isaretleri = [
                bool(re.search(r'(def |class |import |#include|<html|<div|SELECT |function )', s))
                for s in satirlar
            ]
            if sum(kod_isaretleri) >= 2:
                return girdi

        return None
