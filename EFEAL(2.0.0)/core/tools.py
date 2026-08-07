"""
EFEAI Araçlar Modülü
Kod analizi, proje yönetimi, not alma ve diğer araçları birleştiren köprü katmanı.
Brain.py bu modülü kullanarak tüm araçlara erişir.
"""

from typing import Optional
from pathlib import Path

from code_engine.analyzer import kodu_analiz_et, analiz_raporu_formatla, dil_tespit_et
from code_engine.generator import KodUretici
from code_engine.debugger import KodHataAyiklayici
from code_engine.formatter import KodBiçimlendirici
from code_engine.security import GuvenlikTarayici
from workspace_module.project_manager import (
    yeni_proje_olustur, proje_listesi, proje_detayi,
    proje_ilerleme_guncelle, proje_durumu_guncelle,
    gorev_ekle, gorev_tamamla,
)
from workspace_module.file_manager import DosyaYoneticisi
from workspace_module.templates import SablonYoneticisi
from workspace_module.exporter import Dışa_Aktarici
from database import db


class Tools:
    """
    EFEAI araç seti — tüm araçlara tek noktadan erişim.
    """

    def __init__(self):
        self.kod_uretici    = KodUretici()
        self.hata_ayiklayici = KodHataAyiklayici()
        self.bicimlendirici  = KodBiçimlendirici()
        self.guvenlik        = GuvenlikTarayici()
        self.dosya_yoneticisi = DosyaYoneticisi()
        self.sablon_yoneticisi = SablonYoneticisi()
        self.disari_aktarici  = Dışa_Aktarici()

    # ─── Kod Araçları ─────────────────────────────────────────

    def kodu_analiz_et(self, kod: str) -> str:
        """Kodu analiz eder ve rapor döner."""
        rapor = kodu_analiz_et(kod)
        return analiz_raporu_formatla(rapor)

    def kodu_hatayi_bul(self, kod: str, dil: str = None) -> str:
        """Koddaki hataları tespit eder."""
        if not dil:
            dil = dil_tespit_et(kod)
        return self.hata_ayiklayici.hatalar_bul(kod, dil)

    def kodu_bicimlendir(self, kod: str, dil: str = None) -> str:
        """Kodu biçimlendirir."""
        if not dil:
            dil = dil_tespit_et(kod)
        return self.bicimlendirici.bicimlendir(kod, dil)

    def guvenlik_tara(self, kod: str) -> str:
        """Kodda güvenlik açıkları arar."""
        return self.guvenlik.tara(kod)

    def kod_uret(self, istek: str, dil: str = "python") -> str:
        """İstenen kodu üretir."""
        return self.kod_uretici.uret(istek, dil)

    # ─── Proje Araçları ───────────────────────────────────────

    def proje_listele(self) -> str:
        return proje_listesi()

    def proje_olustur(self, isim: str, aciklama: str = "", dil: str = "") -> dict:
        return yeni_proje_olustur(isim, aciklama, dil)

    def proje_detayi_al(self, proje_id: int) -> str:
        return proje_detayi(proje_id)

    def proje_ilerleme(self, proje_id: int, yuzde: int) -> bool:
        return proje_ilerleme_guncelle(proje_id, yuzde)

    def proje_durum(self, proje_id: int, durum: str) -> bool:
        return proje_durumu_guncelle(proje_id, durum)

    def gorev_ekle(self, proje_id: int, baslik: str, oncelik: str = "normal") -> bool:
        return gorev_ekle(proje_id, baslik, oncelik)

    def gorev_tamamla(self, proje_id: int, gorev_id: int) -> bool:
        return gorev_tamamla(proje_id, gorev_id)

    # ─── Not Araçları ─────────────────────────────────────────

    def not_ekle(self, baslik: str, icerik: str, etiketler: list = None) -> int:
        """Yeni not ekler, ID döner."""
        return db.not_ekle(baslik, icerik, etiketler or [])

    def notlari_listele(self) -> str:
        """Notları listeler."""
        notlar = db.not_listele()
        if not notlar:
            return "Henüz kayıtlı not yok."
        satirlar = [f"{'ID':>4}  {'Başlık':<30}  {'Tarih'}"]
        satirlar.append("─" * 55)
        for n in notlar:
            satirlar.append(f"{n['id']:>4}  {n['title'][:28]:<30}  {n.get('created_at','')[:10]}")
        return "\n".join(satirlar)

    def not_ara(self, sorgu: str) -> str:
        """Notlarda arama yapar."""
        notlar = db.not_ara(sorgu)
        if not notlar:
            return f"'{sorgu}' için not bulunamadı."
        sonuclar = [f"🔍 '{sorgu}' için {len(notlar)} not:"]
        for n in notlar[:5]:
            sonuclar.append(f"  [{n['id']}] {n['title']}")
        return "\n".join(sonuclar)

    # ─── İstatistik Araçları ──────────────────────────────────

    def genel_istatistikler(self) -> str:
        """Genel istatistikleri formatlanmış döner."""
        stats = db.genel_istatistikler()
        satirlar = [
            "═══ EFEAI İSTATİSTİKLERİ ═══",
            f"  Projeler         : {stats['proje_sayisi']} (Tamamlanan: {stats['tamamlanan_proje']})",
            f"  Notlar           : {stats['not_sayisi']}",
            f"  Çalışılan Konu   : {stats['calisilan_konu']} (Tamamlanan: {stats['tamamlanan_konu']})",
            f"  Favoriler        : {stats['favori_sayisi']}",
            f"  Toplam Çalışma   : {stats['toplam_calisma_dk']} dakika",
            f"  Toplam Mesaj     : {stats['toplam_mesaj']}",
        ]
        return "\n".join(satirlar)

    # ─── Dosya / Şablon Araçları ──────────────────────────────

    def proje_sablon(self, tur: str) -> str:
        """Proje şablonu döner."""
        return self.sablon_yoneticisi.sablon_al(tur)

    def dosya_listele(self, dizin: str = ".") -> str:
        """Dizin içeriğini listeler."""
        return self.dosya_yoneticisi.listele(dizin)

    def disari_aktar(self, tur: str, hedef: str) -> str:
        """Veriyi dışa aktarır."""
        return self.disari_aktarici.aktar(tur, hedef)
