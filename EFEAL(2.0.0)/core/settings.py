"""
EFEAI Ayarlar Yöneticisi
Uygulama ayarlarını yükler, kaydeder ve günceller.
"""

import json
import os
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "version": "0.1.0",
    "app_name": "EFEAI",
    "motto": "Learn. Build. Improve.",
    "language": "tr",
    "theme": "dark",
    "font_size": "normal",
    "default_mode": "normal",
    "notifications": True,
    "auto_save": True,
    "auto_backup": False,
    "backup_interval_days": 7,
    "conversation_mode": "normal",
    "show_tips": True,
    "show_alternatives": True,
    "teach_mode": True,
    "max_conversation_history": 100,
}


class SettingsManager:
    """Uygulama ayarlarını yönetir."""

    def __init__(self):
        self._settings = {}
        self._yukle()

    def _yukle(self):
        """Ayarları dosyadan yükler. Dosya yoksa varsayılanları kullanır."""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    yuklu = json.load(f)
                # Eksik anahtarları varsayılanlardan tamamla
                self._settings = {**DEFAULT_SETTINGS, **yuklu}
            except (json.JSONDecodeError, IOError):
                self._settings = DEFAULT_SETTINGS.copy()
        else:
            self._settings = DEFAULT_SETTINGS.copy()
            self.kaydet()

    def kaydet(self):
        """Ayarları dosyaya yazar."""
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[AYAR HATASI] Ayarlar kaydedilemedi: {e}")

    def al(self, anahtar: str, varsayilan=None):
        """Belirli bir ayar değeri döner."""
        return self._settings.get(anahtar, varsayilan)

    def guncelle(self, anahtar: str, deger):
        """Belirli bir ayarı günceller ve kaydeder."""
        if anahtar in DEFAULT_SETTINGS:
            self._settings[anahtar] = deger
            self.kaydet()
            return True
        return False

    def tumu(self) -> dict:
        """Tüm ayarları döner."""
        return self._settings.copy()

    def sifirla(self):
        """Ayarları varsayılanlara sıfırlar."""
        self._settings = DEFAULT_SETTINGS.copy()
        self.kaydet()

    def ozet(self) -> str:
        """Ayarların özet metni."""
        satirlar = [
            f"  Sürüm      : {self.al('version')}",
            f"  Tema       : {self.al('theme')}",
            f"  Dil        : {self.al('language')}",
            f"  Mod        : {self.al('conversation_mode')}",
            f"  Öğretici   : {'Açık' if self.al('teach_mode') else 'Kapalı'}",
            f"  Otomatik   : {'Açık' if self.al('auto_save') else 'Kapalı'}",
        ]
        return "\n".join(satirlar)
