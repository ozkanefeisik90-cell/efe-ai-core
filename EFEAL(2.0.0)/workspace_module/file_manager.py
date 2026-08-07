"""
EFEAI Dosya Yöneticisi
Dosya ve dizin işlemlerini yönetir.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


IZIN_VERILEN_UZANTILAR = {
    ".py", ".js", ".ts", ".html", ".css", ".json", ".md", ".txt",
    ".sql", ".yaml", ".yml", ".toml", ".xml", ".csv", ".sh",
    ".java", ".dart", ".c", ".cpp", ".h", ".go", ".rs",
}

DOSYA_IKONU = {
    ".py":   "🐍",
    ".js":   "📜",
    ".ts":   "📘",
    ".html": "🌐",
    ".css":  "🎨",
    ".json": "📋",
    ".md":   "📄",
    ".txt":  "📝",
    ".sql":  "🗄️",
    ".dart": "💙",
    ".java": "☕",
}


class DosyaYoneticisi:
    """
    Güvenli dosya ve dizin işlemleri.
    """

    def __init__(self, kok_dizin: str = "."):
        self.kok = Path(kok_dizin).resolve()

    def listele(self, dizin: str = ".") -> str:
        """Dizin içeriğini formatlanmış döner."""
        hedef = (self.kok / dizin).resolve()
        if not hedef.exists():
            return f"Dizin bulunamadı: {dizin}"
        if not hedef.is_dir():
            return f"Bu bir dizin değil: {dizin}"

        ogeler = sorted(hedef.iterdir())
        if not ogeler:
            return "Dizin boş."

        satirlar = [f"📁 {hedef.name}/", ""]
        for oge in ogeler:
            if oge.name.startswith("."):
                continue
            if oge.is_dir():
                alt_sayisi = len(list(oge.iterdir()))
                satirlar.append(f"  📂 {oge.name}/  ({alt_sayisi} öge)")
            else:
                uzanti = oge.suffix.lower()
                ikon = DOSYA_IKONU.get(uzanti, "📄")
                boyut = self._boyut_formatla(oge.stat().st_size)
                satirlar.append(f"  {ikon} {oge.name}  ({boyut})")

        return "\n".join(satirlar)

    def dosya_oku(self, dosya_yolu: str) -> Optional[str]:
        """Dosya içeriğini okur."""
        yol = (self.kok / dosya_yolu).resolve()
        if not yol.exists():
            return None
        if yol.suffix.lower() not in IZIN_VERILEN_UZANTILAR:
            return "Bu dosya türü okuma için desteklenmiyor."
        try:
            return yol.read_text(encoding="utf-8")
        except Exception as e:
            return f"Dosya okunamadı: {e}"

    def dosya_olustur(self, dosya_yolu: str, icerik: str = "") -> bool:
        """Yeni dosya oluşturur."""
        yol = (self.kok / dosya_yolu).resolve()
        try:
            yol.parent.mkdir(parents=True, exist_ok=True)
            yol.write_text(icerik, encoding="utf-8")
            return True
        except Exception:
            return False

    def dosya_yaz(self, dosya_yolu: str, icerik: str) -> bool:
        """Dosyaya içerik yazar."""
        return self.dosya_olustur(dosya_yolu, icerik)

    def dosya_sil(self, dosya_yolu: str) -> bool:
        """Dosyayı siler."""
        yol = (self.kok / dosya_yolu).resolve()
        try:
            if yol.is_file():
                yol.unlink()
                return True
            return False
        except Exception:
            return False

    def dizin_olustur(self, dizin_yolu: str) -> bool:
        """Dizin oluşturur."""
        yol = (self.kok / dizin_yolu).resolve()
        try:
            yol.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def kopyala(self, kaynak: str, hedef: str) -> bool:
        """Dosya veya dizini kopyalar."""
        kaynak_yol = (self.kok / kaynak).resolve()
        hedef_yol = (self.kok / hedef).resolve()
        try:
            if kaynak_yol.is_file():
                shutil.copy2(str(kaynak_yol), str(hedef_yol))
            else:
                shutil.copytree(str(kaynak_yol), str(hedef_yol))
            return True
        except Exception:
            return False

    def tasi(self, kaynak: str, hedef: str) -> bool:
        """Dosyayı taşır."""
        kaynak_yol = (self.kok / kaynak).resolve()
        hedef_yol = (self.kok / hedef).resolve()
        try:
            shutil.move(str(kaynak_yol), str(hedef_yol))
            return True
        except Exception:
            return False

    def ara(self, desen: str, dizin: str = ".") -> list:
        """Dosya adına göre arama yapar."""
        hedef = (self.kok / dizin).resolve()
        sonuclar = []
        try:
            for yol in hedef.rglob(f"*{desen}*"):
                sonuclar.append(str(yol.relative_to(self.kok)))
        except Exception:
            pass
        return sonuclar[:20]

    def proje_yapisi_goster(self, dizin: str = ".", derinlik: int = 3) -> str:
        """Ağaç yapısında dizin gösterimi."""
        hedef = (self.kok / dizin).resolve()
        if not hedef.exists():
            return "Dizin bulunamadı."
        satirlar = []
        self._agac_ciz(hedef, satirlar, "", derinlik, 0)
        return "\n".join(satirlar)

    def _agac_ciz(self, dizin: Path, satirlar: list, prefix: str,
                  maks_derinlik: int, mevcut_derinlik: int):
        if mevcut_derinlik > maks_derinlik:
            return
        ogeler = sorted(dizin.iterdir(), key=lambda x: (x.is_file(), x.name))
        ogeler = [o for o in ogeler if not o.name.startswith(".")]
        for i, oge in enumerate(ogeler):
            son_mu = (i == len(ogeler) - 1)
            baglanti = "└── " if son_mu else "├── "
        
            if oge.is_dir():
                satirlar.append(f"{prefix}{baglanti}📂 {oge.name}/")
                uzanti = "    " if son_mu else "│   "
                self._agac_ciz(oge, satirlar, prefix + uzanti,
                               maks_derinlik, mevcut_derinlik + 1)
            else:
                uzanti_ikon = DOSYA_IKONU.get(oge.suffix.lower(), "📄")
                satirlar.append(f"{prefix}{baglanti}{uzanti_ikon} {oge.name}")

    def _boyut_formatla(self, bayt: int) -> str:
        """Dosya boyutunu formatlar."""
        if bayt < 1024:
            return f"{bayt}B"
        elif bayt < 1024 * 1024:
            return f"{bayt // 1024}KB"
        else:
            return f"{bayt // (1024*1024)}MB"
