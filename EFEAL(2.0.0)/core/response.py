"""
EFEAI Yanıt Oluşturma Modülü
Ham verileri alır, karakter motoruyla biçimlendirir ve son yanıtı üretir.
Tanım → Örnek → Benzetme → Kod → İpucu sırasını uygular.
"""

from typing import Optional
from core.character_engine import CharacterEngine, ConversationMode


class ResponseBuilder:
    """
    EFEAI yanıtlarını yapılandırılmış biçimde oluşturur.
    Sıra: Tanım → Örnek → Benzetme → Kod → İpucu
    """

    def __init__(self, karakter: CharacterEngine):
        self.karakter = karakter

    # ─── Ana Yanıt Üretici ────────────────────────────────────

    def bilgi_yaniti(self, veri: dict, kisa: bool = False) -> str:
        """
        Bilgi tabanından gelen veriyi kullanıcıya sunar.
        Sıra: Tanım → Örnek → Benzetme → Kod → İpucu
        """
        if not veri:
            return self.karakter.bilmiyorum_yaniti()

        parcalar = []

        # Açılış
        acilis = self.karakter.acilis_cumle()
        parcalar.append(acilis)
        parcalar.append("")

        # 1. Tanım
        tanim = self._tanim_bul(veri)
        if tanim:
            parcalar.append(f"📌 {tanim}")
            parcalar.append("")

        if kisa:
            return "\n".join(p for p in parcalar if p is not None)

        # 2. Örnek
        ornekler = veri.get("examples", [])
        if ornekler:
            ilk_ornek = ornekler[0]
            if isinstance(ilk_ornek, dict):
                baslik = ilk_ornek.get("title", "Örnek")
                kod = ilk_ornek.get("code", ilk_ornek.get("template", ""))
                aciklama = ilk_ornek.get("description", "")
                if kod:
                    parcalar.append(f"💡 Örnek — {baslik}")
                    if aciklama:
                        parcalar.append(f"   {aciklama}")
                    parcalar.append(f"```\n{kod}\n```")
                    parcalar.append("")
            elif isinstance(ilk_ornek, str):
                parcalar.append(f"💡 Örnek:")
                parcalar.append(f"```\n{ilk_ornek}\n```")
                parcalar.append("")

        # 3. Benzetme / İpucu
        ipuclari = veri.get("tips", [])
        if ipuclari:
            ipucu = ipuclari[0]
            if isinstance(ipucu, dict):
                ipucu_metni = ipucu.get("tip", str(ipucu))
            else:
                ipucu_metni = str(ipucu)
            parcalar.append(f"💬 İpucu: {ipucu_metni}")
            parcalar.append("")

        # 4. Sık hatalar
        hatalar = veri.get("errors", [])
        if hatalar:
            ilk_hata = hatalar[0]
            if isinstance(ilk_hata, dict):
                sorun = ilk_hata.get("problem", "")
                cozum = ilk_hata.get("solution", "")
                if sorun:
                    parcalar.append(f"⚠️  Sık Hata: {sorun}")
                    if cozum:
                        parcalar.append(f"   ✅ Çözüm: {cozum}")
                    parcalar.append("")

        # 5. İlgili konular
        ilgili = veri.get("related_topics", [])
        if ilgili:
            ilgili_str = ", ".join(ilgili[:4])
            parcalar.append(f"🔗 İlgili Konular: {ilgili_str}")
            parcalar.append("")

        # Öğretici kapanış
        ogretici = self.karakter.ogretici_kapanisi()
        parcalar.append(f"→ {ogretici}")

        return "\n".join(p for p in parcalar if p is not None)

    def hata_yaniti(self, hatalar: list) -> str:
        """Hata listesini kullanıcıya sunar."""
        if not hatalar:
            return "Bu konuda bilinen bir hata kaydı bulunamadı."

        parcalar = [self.karakter.hata_bildirimi("")]
        for i, hata in enumerate(hatalar[:3], 1):
            if isinstance(hata, dict):
                sorun = hata.get("problem", "")
                cozum = hata.get("solution", "")
                parcalar.append(f"{i}. ❌ {sorun}")
                if cozum:
                    parcalar.append(f"   ✅ {cozum}")
        return "\n".join(parcalar)

    def ornek_yaniti(self, ornekler: list, baslik: str = "") -> str:
        """Örnek kodu kullanıcıya sunar."""
        if not ornekler:
            return "Bu konu için örnek bulunamadı."

        parcalar = []
        if baslik:
            parcalar.append(f"📂 {baslik} — Örnekler")
            parcalar.append("")

        for ornek in ornekler[:2]:
            if isinstance(ornek, dict):
                parcalar.append(f"• {ornek.get('title', 'Örnek')}")
                aciklama = ornek.get("description", "")
                if aciklama:
                    parcalar.append(f"  {aciklama}")
                kod = ornek.get("code", ornek.get("template", ""))
                if kod:
                    parcalar.append(f"```\n{kod}\n```")
            elif isinstance(ornek, str):
                parcalar.append(f"```\n{ornek}\n```")
            parcalar.append("")

        ogretici = self.karakter.ogretici_kapanisi()
        parcalar.append(f"→ {ogretici}")
        return "\n".join(parcalar)

    def ipucu_yaniti(self, ipuclari: list) -> str:
        """İpuçları listesini kullanıcıya sunar."""
        if not ipuclari:
            return "Bu konu için ipucu bulunamadı."

        parcalar = ["💡 İpuçları:"]
        for i, ipucu in enumerate(ipuclari[:5], 1):
            if isinstance(ipucu, dict):
                tip = ipucu.get("tip", "")
                kategori = ipucu.get("category", "")
                ek = f" [{kategori}]" if kategori else ""
                parcalar.append(f"  {i}.{ek} {tip}")
            else:
                parcalar.append(f"  {i}. {ipucu}")
        return "\n".join(parcalar)

    def konu_listesi_yaniti(self, konular: list) -> str:
        """Mevcut konuları tablo formatında sunar."""
        if not konular:
            return "Bilgi tabanında henüz konu yok."

        parcalar = ["📚 Bilgi Tabanı — Mevcut Konular", ""]
        for k in konular:
            konu_adi = k.get("konu", k.get("dosya", "?"))
            zorluk = k.get("zorluk", "")
            ek = f"  [{zorluk}]" if zorluk else ""
            parcalar.append(f"  • {konu_adi}{ek}")

        parcalar.append("")
        parcalar.append("Bir konu hakkında bilgi almak için 'X nedir' veya 'X anlat' yaz.")
        return "\n".join(parcalar)

    def genel_arama_yaniti(self, sonuclar: list, sorgu: str) -> str:
        """Genel arama sonuçlarını kullanıcıya sunar."""
        if not sonuclar:
            return (
                f"'{sorgu}' için bilgi tabanımda yeterli sonuç bulunamadı.\n"
                "Konuyu farklı kelimelerle ifade etmeyi deneyebilirsin."
            )

        parcalar = [f"🔍 '{sorgu}' için bulunanlar:", ""]
        for s in sonuclar[:3]:
            konu = s.get("konu", "")
            ilgili = s.get("ilgili_tanim", s.get("definition", ""))
            if isinstance(ilgili, dict):
                ilgili = ilgili.get("content", "")
            if ilgili and len(str(ilgili)) > 150:
                ilgili = str(ilgili)[:150] + "..."
            parcalar.append(f"  📌 {konu}")
            if ilgili:
                parcalar.append(f"     {ilgili}")
            parcalar.append("")

        return "\n".join(parcalar)

    def karsilastirma_yaniti(self, a: str, b: str, veri_a: dict, veri_b: dict) -> str:
        """İki konuyu karşılaştırır."""
        def tanim_al(v: dict) -> str:
            if not v:
                return "Bilgi bulunamadı."
            d = v.get("definitions", [])
            if d and isinstance(d[0], dict):
                return d[0].get("content", "")[:200]
            elif d:
                return str(d[0])[:200]
            return v.get("definition", "")[:200]

        parcalar = [
            f"⚖️  {a} vs {b}",
            "",
            f"▶ {a}:",
            f"  {tanim_al(veri_a)}",
            "",
            f"▶ {b}:",
            f"  {tanim_al(veri_b)}",
            "",
        ]
        return "\n".join(parcalar)

    # ─── Yardımcılar ──────────────────────────────────────────

    def _tanim_bul(self, veri: dict) -> str:
        """Veriden birincil tanımı bulur."""
        # Definitions listesi
        tanımlar = veri.get("definitions", [])
        if tanımlar:
            ilk = tanımlar[0]
            if isinstance(ilk, dict):
                return ilk.get("content", "")
            return str(ilk)

        # Doğrudan definition alanı
        tanim = veri.get("definition", "")
        if tanim:
            return tanim

        return ""

    def ozet_yaniti(self, veri: dict) -> str:
        """Kısa özet yanıtı üretir."""
        tanim = self._tanim_bul(veri)
        if not tanim:
            return self.karakter.bilmiyorum_yaniti()
        # İlk 2 cümle
        cumleler = tanim.split(".")
        kisa = ". ".join(cumleler[:2]).strip()
        if kisa and not kisa.endswith("."):
            kisa += "."
        return kisa
