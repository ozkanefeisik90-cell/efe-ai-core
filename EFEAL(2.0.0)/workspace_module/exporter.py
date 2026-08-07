"""
EFEAI Dışa Aktarıcı
Proje verisi, not ve konuşma geçmişini farklı formatlara aktarır.
"""

import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from database import db


class Dışa_Aktarici:
    """
    Verileri farklı formatlara aktarır.
    Desteklenen: JSON, TXT, ZIP
    """

    def __init__(self):
        self.disa_aktar_dizini = Path("backup")
        self.disa_aktar_dizini.mkdir(exist_ok=True)

    def aktar(self, tur: str, hedef: str = None) -> str:
        """Belirtilen türde dışa aktarma yapar."""
        tur = tur.lower()
        zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not hedef:
            hedef = str(self.disa_aktar_dizini / f"efeai_{tur}_{zaman_damgasi}")

        if tur == "projeler":
            return self._projeler_aktar(hedef)
        elif tur == "notlar":
            return self._notlar_aktar(hedef)
        elif tur == "konuşmalar" or tur == "konusmalar":
            return self._konusmalar_aktar(hedef)
        elif tur == "tümü" or tur == "tumu" or tur == "hepsi":
            return self._tumu_aktar(hedef)
        elif tur == "zip":
            return self._zip_olustur(hedef)
        else:
            return f"Bilinmeyen dışa aktarma türü: '{tur}'. Mevcut: projeler, notlar, konuşmalar, tümü, zip"

    def _projeler_aktar(self, hedef: str) -> str:
        """Projeleri JSON olarak aktarır."""
        projeler = db.proje_listele()
        dosya = Path(hedef + ".json")
        veri = {
            "disa_aktarma_tarihi": datetime.now().isoformat(),
            "toplam": len(projeler),
            "projeler": [dict(p) for p in projeler],
        }
        dosya.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")
        return f"✅ {len(projeler)} proje aktarıldı → {dosya.name}"

    def _notlar_aktar(self, hedef: str) -> str:
        """Notları JSON ve TXT olarak aktarır."""
        notlar = db.not_listele()
        dosya_json = Path(hedef + ".json")
        dosya_txt  = Path(hedef + ".txt")

        veri = {
            "disa_aktarma_tarihi": datetime.now().isoformat(),
            "toplam": len(notlar),
            "notlar": [dict(n) for n in notlar],
        }
        dosya_json.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")

        # TXT versiyonu
        satirlar = [f"EFEAI Notları — {datetime.now().strftime('%d.%m.%Y')}", "=" * 50, ""]
        for n in notlar:
            satirlar.append(f"[{n['id']}] {n['title']}")
            satirlar.append(f"Tarih: {n.get('created_at','')[:10]}")
            satirlar.append(n.get("content", ""))
            satirlar.append("─" * 30)
        dosya_txt.write_text("\n".join(satirlar), encoding="utf-8")

        return f"✅ {len(notlar)} not aktarıldı → {dosya_json.name} + {dosya_txt.name}"

    def _konusmalar_aktar(self, hedef: str) -> str:
        """Konuşma geçmişini aktarır."""
        gecmis = db.konusma_gecmisi(limit=1000)
        dosya = Path(hedef + ".json")
        veri = {
            "disa_aktarma_tarihi": datetime.now().isoformat(),
            "toplam_mesaj": len(gecmis),
            "konusmalar": [dict(k) for k in gecmis],
        }
        dosya.write_text(json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8")
        return f"✅ {len(gecmis)} mesaj aktarıldı → {dosya.name}"

    def _tumu_aktar(self, hedef: str) -> str:
        """Tüm verileri aktarır."""
        sonuclar = []
        sonuclar.append(self._projeler_aktar(hedef + "_projeler"))
        sonuclar.append(self._notlar_aktar(hedef + "_notlar"))
        sonuclar.append(self._konusmalar_aktar(hedef + "_konusmalar"))
        return "\n".join(sonuclar)

    def _zip_olustur(self, hedef: str) -> str:
        """Tüm EFEAI verilerini ZIP olarak paketler."""
        zip_yolu = Path(hedef + ".zip")
        kok = Path(__file__).parent.parent

        dahil_edilecekler = [
            "core", "code_engine", "knowledge_base", "workspace_module",
            "academy", "database", "main.py", "settings.json",
            "requirements.txt", "README.md",
        ]

        with zipfile.ZipFile(zip_yolu, "w", zipfile.ZIP_DEFLATED) as zf:
            for oge in dahil_edilecekler:
                yol = kok / oge
                if yol.is_file():
                    zf.write(yol, f"EFEAI/{oge}")
                elif yol.is_dir():
                    for alt in yol.rglob("*"):
                        if "__pycache__" in str(alt) or alt.suffix == ".pyc":
                            continue
                        zf.write(alt, f"EFEAI/{alt.relative_to(kok)}")

        boyut_kb = zip_yolu.stat().st_size // 1024
        return f"✅ ZIP yedek oluşturuldu → {zip_yolu.name} ({boyut_kb}KB)"

    def istatistik_raporu(self) -> str:
        """İstatistik raporu üretir."""
        stats = db.genel_istatistikler()
        zaman = datetime.now().strftime("%d.%m.%Y %H:%M")
        satirlar = [
            f"═══ EFEAI İstatistik Raporu — {zaman} ═══",
            f"  Toplam Proje      : {stats['proje_sayisi']}",
            f"  Tamamlanan Proje  : {stats['tamamlanan_proje']}",
            f"  Toplam Not        : {stats['not_sayisi']}",
            f"  Çalışılan Konu    : {stats['calisilan_konu']}",
            f"  Tamamlanan Konu   : {stats['tamamlanan_konu']}",
            f"  Toplam Çalışma    : {stats['toplam_calisma_dk']} dakika",
            f"  Toplam Mesaj      : {stats['toplam_mesaj']}",
        ]
        return "\n".join(satirlar)
