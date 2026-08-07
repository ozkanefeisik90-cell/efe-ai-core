"""
EFEAI Proje Yöneticisi
Proje oluşturma, listeleme, görev takibi ve ilerleme yönetimi.
"""

import textwrap
from database import db


DURUM_SEMBOLLERI = {
    "Planlanıyor":    "🟢",
    "Geliştiriliyor": "🟡",
    "Test Ediliyor":  "🔵",
    "Tamamlandı":     "⚪",
    "Arşivlendi":     "⚫",
}

PROJE_TURLERI = [
    "Mobil Uygulama",
    "Web Uygulaması",
    "Masaüstü Uygulaması",
    "API / Backend",
    "Kütüphane / Araç",
    "Veri Analizi",
    "Yapay Zekâ",
    "Oyun",
    "Diğer",
]


def yeni_proje_olustur(isim: str, aciklama: str = "", dil: str = "",
                        teknolojiler: list = None, tur: str = "") -> dict:
    """Yeni bir proje oluşturur ve veritabanına kaydeder."""
    pid = db.proje_olustur(isim, aciklama, dil, teknolojiler or [], tur)
    return {"basarili": True, "proje_id": pid, "isim": isim}


def proje_listesi(durum: str = None) -> str:
    """Projeleri tablo formatında döner."""
    projeler = db.proje_listele(durum)
    if not projeler:
        return "Henüz kayıtlı proje yok."

    satirlar = []
    satirlar.append(f"{'ID':>4}  {'İsim':<22} {'Dil':<12} {'Durum':<18} {'İlerleme':>8}")
    satirlar.append("─" * 68)

    for p in projeler:
        sembol = DURUM_SEMBOLLERI.get(p["status"], "○")
        ilerleme = f"%{p.get('progress', 0)}"
        isim = p["name"][:20]
        dil = (p.get("language") or "—")[:10]
        durum = f"{sembol} {p['status']}"[:17]
        satirlar.append(f"{p['id']:>4}  {isim:<22} {dil:<12} {durum:<18} {ilerleme:>8}")

    return "\n".join(satirlar)


def proje_detayi(proje_id: int) -> str:
    """Bir projenin detaylı bilgilerini formatlar."""
    p = db.proje_al(proje_id)
    if not p:
        return f"Proje bulunamadı (ID: {proje_id})"

    teknolojiler = ", ".join(p.get("technologies") or []) or "Belirtilmemiş"
    sembol = DURUM_SEMBOLLERI.get(p["status"], "○")
    ilerleme_bar = _ilerleme_bar(p.get("progress", 0))

    satirlar = [
        f"═══ {p['name'].upper()} ═══",
        f"Tür         : {p.get('project_type') or '—'}",
        f"Dil         : {p.get('language') or '—'}",
        f"Teknolojiler: {teknolojiler}",
        f"Durum       : {sembol} {p['status']}",
        f"İlerleme    : {ilerleme_bar} %{p.get('progress', 0)}",
        f"Oluşturulma : {p.get('created_at', '—')[:10]}",
        f"Güncelleme  : {p.get('updated_at', '—')[:10]}",
    ]

    if p.get("description"):
        aciklama = textwrap.fill(p["description"], width=60, initial_indent="  ", subsequent_indent="  ")
        satirlar.append(f"Açıklama:\n{aciklama}")

    if p.get("notes"):
        satirlar.append(f"Notlar: {p['notes']}")

    # Görevler
    gorevler = db.proje_gorevleri(proje_id)
    if gorevler:
        satirlar.append("\nGörevler:")
        for g in gorevler:
            isaret = "☑" if g["done"] else "☐"
            satirlar.append(f"  {isaret} [{g.get('priority','normal'):>6}] {g['title']}")

    # Son loglar
    loglar = db.proje_log_al(proje_id)
    if loglar:
        satirlar.append("\nSon Aktivite:")
        for log in loglar[:5]:
            tarih = log["logged_at"][:10]
            satirlar.append(f"  {tarih} — {log['log_entry']}")

    return "\n".join(satirlar)


def _ilerleme_bar(yuzde: int, genislik: int = 20) -> str:
    """Metin tabanlı ilerleme çubuğu."""
    dolu = int((yuzde / 100) * genislik)
    bos = genislik - dolu
    return f"[{'█' * dolu}{'░' * bos}]"


def proje_ilerleme_guncelle(proje_id: int, yuzde: int) -> bool:
    """Proje ilerleme yüzdesini günceller."""
    yuzde = max(0, min(100, yuzde))
    return db.proje_guncelle(proje_id, progress=yuzde)


def proje_durumu_guncelle(proje_id: int, yeni_durum: str) -> bool:
    """Proje durumunu değiştirir."""
    gecerli_durumlar = list(DURUM_SEMBOLLERI.keys())
    if yeni_durum not in gecerli_durumlar:
        return False
    return db.proje_guncelle(proje_id, status=yeni_durum)


def gorev_ekle(proje_id: int, baslik: str, oncelik: str = "normal") -> int:
    """Projeye görev ekler."""
    return db.gorev_ekle(proje_id, baslik, oncelik)


def gorev_tamamla(gorev_id: int):
    """Görevi tamamlandı olarak işaretler."""
    db.gorev_tamamla(gorev_id)
    return True


def proje_klasor_yapisi_olustur(proje_tur: str, proje_adi: str) -> str:
    """Proje türüne göre önerilen klasör yapısını döner."""
    yapılar = {
        "Web Uygulaması": f"""{proje_adi}/
├── index.html
├── about.html
├── css/
│   └── style.css
├── js/
│   └── app.js
├── images/
└── assets/""",

        "Mobil Uygulama": f"""{proje_adi}/
├── lib/
│   ├── main.dart
│   ├── pages/
│   │   ├── home_page.dart
│   │   └── settings_page.dart
│   ├── widgets/
│   │   └── custom_button.dart
│   ├── models/
│   ├── services/
│   └── database/
├── assets/
│   ├── images/
│   └── fonts/
└── pubspec.yaml""",

        "API / Backend": f"""{proje_adi}/
├── main.py
├── routes/
│   ├── __init__.py
│   └── api.py
├── models/
│   ├── __init__.py
│   └── models.py
├── database/
│   └── db.py
├── utils/
│   └── helpers.py
├── tests/
└── requirements.txt""",

        "Veri Analizi": f"""{proje_adi}/
├── notebooks/
│   └── analiz.ipynb
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
│   └── analiz.py
├── outputs/
│   └── grafikler/
└── requirements.txt""",
    }

    return yapılar.get(proje_tur, f"""{proje_adi}/
├── src/
├── docs/
├── tests/
└── README.md""")


def proje_istatistikleri() -> str:
    """Tüm projelerin özet istatistiklerini döner."""
    istatistik = db.genel_istatistikler()
    projeler = db.proje_listele()

    durum_sayilari = {}
    for p in projeler:
        d = p["status"]
        durum_sayilari[d] = durum_sayilari.get(d, 0) + 1

    satirlar = [
        "═══ PROJE İSTATİSTİKLERİ ═══",
        f"Toplam Proje   : {istatistik['proje_sayisi']}",
        f"Tamamlanan     : {istatistik['tamamlanan_proje']}",
    ]
    for durum, sembol in DURUM_SEMBOLLERI.items():
        adet = durum_sayilari.get(durum, 0)
        if adet > 0:
            satirlar.append(f"  {sembol} {durum:<16}: {adet}")

    return "\n".join(satirlar)
