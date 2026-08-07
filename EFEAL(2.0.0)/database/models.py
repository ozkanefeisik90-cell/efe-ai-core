"""
EFEAI Veritabanı Modelleri
SQLite tablolarının Python veri sınıfları ile temsili.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Konusma:
    """Konuşma geçmişi kaydı."""
    id: int = 0
    session_id: str = ""
    rol: str = "user"              # 'user' | 'efeai'
    mesaj: str = ""
    konu: Optional[str] = None
    mod: str = "normal"
    zaman: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if self.rol not in ("user", "efeai"):
            raise ValueError(f"Geçersiz rol: {self.rol}")


@dataclass
class Proje:
    """Proje kaydı."""
    id: int = 0
    isim: str = ""
    aciklama: Optional[str] = None
    dil: Optional[str] = None
    teknolojiler: List[str] = field(default_factory=list)
    proje_turu: Optional[str] = None
    durum: str = "Planlanıyor"
    ilerleme: int = 0
    notlar: Optional[str] = None
    klasor_yolu: Optional[str] = None
    olusturulma: str = field(default_factory=lambda: datetime.now().isoformat())
    guncelleme: str = field(default_factory=lambda: datetime.now().isoformat())

    GECERLI_DURUMLAR = ("Planlanıyor", "Geliştiriliyor", "Test Ediliyor", "Tamamlandı", "Arşivlendi")

    def gecerli_mi(self) -> bool:
        return bool(self.isim) and self.durum in self.GECERLI_DURUMLAR

    def ilerleme_cubugu(self, genislik: int = 20) -> str:
        """Metin tabanlı ilerleme çubuğu."""
        dolu = int((self.ilerleme / 100) * genislik)
        bos = genislik - dolu
        return f"[{'█' * dolu}{'░' * bos}] %{self.ilerleme}"


@dataclass
class ProjeGorev:
    """Proje görevi."""
    id: int = 0
    proje_id: int = 0
    baslik: str = ""
    tamamlandi: bool = False
    oncelik: str = "normal"        # 'düşük' | 'normal' | 'yüksek'
    olusturulma: str = field(default_factory=lambda: datetime.now().isoformat())
    tamamlanma: Optional[str] = None

    def tamamla(self):
        self.tamamlandi = True
        self.tamamlanma = datetime.now().isoformat()


@dataclass
class OgrenmeIlerlemesi:
    """Öğrenme ilerlemesi kaydı."""
    id: int = 0
    konu: str = ""
    alt_konu: Optional[str] = None
    durum: str = "Okunmadı"        # 'Okunmadı' | 'İncelendi' | 'Öğreniliyor' | 'Tamamlandı'
    puan: int = 0
    calisma_dakika: int = 0
    son_calisma: Optional[str] = None
    tekrar_tarihi: Optional[str] = None
    notlar: Optional[str] = None

    GECERLI_DURUMLAR = ("Okunmadı", "İncelendi", "Öğreniliyor", "Tamamlandı")

    def tamamlandi_mi(self) -> bool:
        return self.durum == "Tamamlandı"

    def ilerleme_yuzdesi(self) -> int:
        """Duruma göre yüzde döner."""
        yuzdeler = {"Okunmadı": 0, "İncelendi": 25, "Öğreniliyor": 60, "Tamamlandı": 100}
        return yuzdeler.get(self.durum, 0)


@dataclass
class Not:
    """Kişisel not kaydı."""
    id: int = 0
    baslik: str = ""
    icerik: str = ""
    etiketler: List[str] = field(default_factory=list)
    favori: bool = False
    olusturulma: str = field(default_factory=lambda: datetime.now().isoformat())
    guncelleme: str = field(default_factory=lambda: datetime.now().isoformat())

    def ozet(self, maks_uzunluk: int = 100) -> str:
        """İçeriğin kısa özetini döner."""
        return self.icerik[:maks_uzunluk] + "..." if len(self.icerik) > maks_uzunluk else self.icerik


@dataclass
class Favori:
    """Favori içerik kaydı."""
    id: int = 0
    konu: str = ""
    tur: str = "konu"              # 'konu' | 'etiketi' | 'ornek'
    not_metni: Optional[str] = None
    olusturulma: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AppLog:
    """Uygulama log kaydı."""
    id: int = 0
    seviye: str = "info"           # 'debug' | 'info' | 'warning' | 'error'
    mesaj: str = ""
    detay: Optional[str] = None
    zaman: str = field(default_factory=lambda: datetime.now().isoformat())
