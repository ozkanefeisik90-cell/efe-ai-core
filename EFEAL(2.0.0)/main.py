#!/usr/bin/env python3
"""
EFEAI — Kişisel Teknoloji Yapay Zekâ Sistemi
"Learn. Build. Improve."

Kullanım: python main.py
"""

import os
import sys
import textwrap
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

# Proje kök dizinini sys.path'e ekle
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# ─── Renkli Terminal Çıktısı ─────────────────────────────────

class Renk:
    RESET   = "\033[0m"
    KALIN   = "\033[1m"
    MAVI    = "\033[34m"
    CYAN    = "\033[36m"
    YESIL   = "\033[32m"
    SARI    = "\033[33m"
    KIRMIZI = "\033[31m"
    GRI     = "\033[90m"
    BEYAZ   = "\033[97m"

def r(metin: str, renk: str = "") -> str:
    """Renkli metin döner."""
    return f"{renk}{metin}{Renk.RESET}"

def _renk_destekleniyor() -> bool:
    """Terminal renk desteği var mı?"""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


# ─── Başlangıç Ekranı ─────────────────────────────────────────

BANNER = r"""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║    ███████╗███████╗███████╗ █████╗ ██╗                ║
║    ██╔════╝██╔════╝██╔════╝██╔══██╗██║                ║
║    █████╗  █████╗  █████╗  ███████║██║                ║
║    ██╔══╝  ██╔══╝  ██╔══╝  ██╔══██║██║                ║
║    ███████╗██║     ███████╗██║  ██║██║                ║
║    ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝                ║
║                                                       ║
║         Kişisel Teknoloji Yapay Zekâ Sistemi          ║
║              "Learn. Build. Improve."                 ║
║                                                       ║
║    Versiyon: 0.1.0  |  Python + SQLite  |  Offline   ║
╚═══════════════════════════════════════════════════════╝
"""


# ─── Gecikmeli Import (hata mesajı için) ──────────────────────

def _sistemi_baslat():
    """Tüm modülleri başlatır."""
    from database import db
    db.tablolari_olustur()

    from core.brain import Brain
    return Brain()


# ─── Yardımcı Fonksiyonlar ────────────────────────────────────

def _ayrac(genislik: int = 60, karakter: str = "─") -> str:
    return karakter * genislik


def _formatlı_yazdir(metin: str, girinti: int = 0):
    """Uzun metinleri terminal genişliğine göre sarar ve yazar."""
    prefix = " " * girinti
    for satir in metin.splitlines():
        if satir.strip() == "":
            print()
        else:
            print(prefix + satir)


def _kullanici_prompt() -> str:
    """Kullanıcı giriş istemine uygun format."""
    return f"\n{r('Sen', Renk.CYAN)} › "


def _efeai_header() -> str:
    return f"\n{r('EFEAI', Renk.MAVI + Renk.KALIN)} › "


# ─── Alt Menüler ──────────────────────────────────────────────

def _proje_menusu():
    """Proje yönetimi alt menüsü."""
    from workspace_module.project_manager import (
        yeni_proje_olustur, proje_listesi, proje_detayi,
        proje_ilerleme_guncelle, proje_durumu_guncelle,
        gorev_ekle, gorev_tamamla, proje_klasor_yapisi_olustur,
        proje_istatistikleri, DURUM_SEMBOLLERI, PROJE_TURLERI
    )

    while True:
        print(f"\n{r('── PROJE YÖNETİCİSİ ──', Renk.SARI)}")
        print("  1. Proje listesi")
        print("  2. Yeni proje oluştur")
        print("  3. Proje detayı")
        print("  4. İlerleme güncelle")
        print("  5. Durum değiştir")
        print("  6. Görev ekle")
        print("  7. Görev tamamla")
        print("  8. Klasör yapısı öner")
        print("  9. İstatistikler")
        print("  0. Ana menüye dön")

        secim = input("\n  Seçim: ").strip()

        if secim == "0":
            break
        elif secim == "1":
            print("\n" + proje_listesi())
        elif secim == "2":
            isim = input("  Proje adı: ").strip()
            if not isim:
                print("  Proje adı boş olamaz.")
                continue
            aciklama = input("  Açıklama: ").strip()
            dil = input("  Programlama dili: ").strip()
            print("  Proje türleri: " + ", ".join(PROJE_TURLERI))
            tur = input("  Tür: ").strip()
            techs_str = input("  Teknolojiler (virgülle ayır): ").strip()
            techs = [t.strip() for t in techs_str.split(",") if t.strip()]
            sonuc = yeni_proje_olustur(isim, aciklama, dil, techs, tur)
            print(f"  ✓ Proje oluşturuldu (ID: {sonuc['proje_id']})")
        elif secim == "3":
            pid = input("  Proje ID: ").strip()
            if pid.isdigit():
                print("\n" + proje_detayi(int(pid)))
        elif secim == "4":
            pid = input("  Proje ID: ").strip()
            yuzde = input("  İlerleme (%): ").strip()
            if pid.isdigit() and yuzde.isdigit():
                proje_ilerleme_guncelle(int(pid), int(yuzde))
                print(f"  ✓ İlerleme güncellendi: %{yuzde}")
        elif secim == "5":
            pid = input("  Proje ID: ").strip()
            durumlar = list(DURUM_SEMBOLLERI.keys())
            print("  Durumlar: " + " | ".join(durumlar))
            yeni = input("  Yeni durum: ").strip()
            if pid.isdigit():
                if proje_durumu_guncelle(int(pid), yeni):
                    print(f"  ✓ Durum güncellendi: {yeni}")
                else:
                    print("  Geçersiz durum.")
        elif secim == "6":
            pid = input("  Proje ID: ").strip()
            baslik = input("  Görev başlığı: ").strip()
            if pid.isdigit() and baslik:
                gorev_ekle(int(pid), baslik)
                print("  ✓ Görev eklendi.")
        elif secim == "7":
            gid = input("  Görev ID: ").strip()
            if gid.isdigit():
                gorev_tamamla(int(gid))
                print("  ✓ Görev tamamlandı.")
        elif secim == "8":
            print("  Proje türleri: " + ", ".join(PROJE_TURLERI))
            tur = input("  Tür: ").strip()
            isim = input("  Proje adı: ").strip() or "proje"
            print("\n" + proje_klasor_yapisi_olustur(tur, isim))
        elif secim == "9":
            print("\n" + proje_istatistikleri())


def _akademi_menusu():
    """Academy alt menüsü."""
    from academy.academy import (
        ogrenme_haritasi_goster, quiz_yap,
        gunluk_plan_olustur, istatistikler,
        konu_tamamla, konu_incele
    )

    while True:
        print(f"\n{r('── EFEAI ACADEMY ──', Renk.SARI)}")
        print("  1. Öğrenme haritası")
        print("  2. Günlük çalışma planı")
        print("  3. Quiz")
        print("  4. Konuyu tamamlandı işaretle")
        print("  5. Konuyu incelendi işaretle")
        print("  6. İstatistikler")
        print("  0. Ana menüye dön")

        secim = input("\n  Seçim: ").strip()

        if secim == "0":
            break
        elif secim == "1":
            print("\n" + ogrenme_haritasi_goster())
        elif secim == "2":
            dk = input("  Kaç dakika müsaitsin? [50]: ").strip()
            dk = int(dk) if dk.isdigit() else 50
            print("\n" + gunluk_plan_olustur(dk))
        elif secim == "3":
            konu = input("  Quiz konusu (HTML / Python / Git): ").strip()
            print("\n" + quiz_yap(konu))
        elif secim == "4":
            konu = input("  Konu adı: ").strip()
            sure = input("  Çalışma süresi (dk): ").strip()
            konu_tamamla(konu, int(sure) if sure.isdigit() else 0)
            print(f"  ✓ '{konu}' tamamlandı olarak işaretlendi.")
        elif secim == "5":
            konu = input("  Konu adı: ").strip()
            konu_incele(konu)
            print(f"  ✓ '{konu}' incelendi olarak işaretlendi.")
        elif secim == "6":
            print("\n" + istatistikler())


def _notlar_menusu():
    """Kişisel notlar alt menüsü."""
    from database import db

    while True:
        print(f"\n{r('── KİŞİSEL NOTLAR ──', Renk.SARI)}")
        print("  1. Notları listele")
        print("  2. Yeni not ekle")
        print("  3. Not sil")
        print("  0. Ana menüye dön")

        secim = input("\n  Seçim: ").strip()

        if secim == "0":
            break
        elif secim == "1":
            notlar = db.not_listele()
            if not notlar:
                print("  Henüz not yok.")
            else:
                for n in notlar:
                    print(f"\n  [{n['id']}] {n['title']} ({n.get('topic') or 'Genel'})")
                    print(f"      {n['content'][:80]}{'...' if len(n['content']) > 80 else ''}")
        elif secim == "2":
            baslik = input("  Not başlığı: ").strip()
            konu = input("  Konu (opsiyonel): ").strip()
            print("  Not içeriği (bitirmek için boş satır bırak):")
            satirlar = []
            while True:
                satir = input("  > ")
                if not satir:
                    break
                satirlar.append(satir)
            if baslik and satirlar:
                not_id = db.not_ekle(baslik, "\n".join(satirlar), konu or None)
                print(f"  ✓ Not kaydedildi (ID: {not_id})")
        elif secim == "3":
            not_id = input("  Not ID: ").strip()
            if not_id.isdigit():
                db.not_sil(int(not_id))
                print("  ✓ Not silindi.")


def _yedek_olustur():
    """Tüm veritabanı ve ayarları ZIP olarak yedekler."""
    tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
    yedek_adi = f"efeai_yedek_{tarih}.zip"
    yedek_yolu = BASE_DIR / "backup" / yedek_adi

    yedek_yolu.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(yedek_yolu, "w", zipfile.ZIP_DEFLATED) as zf:
        # Veritabanı
        db_yolu = BASE_DIR / "database" / "efeai.db"
        if db_yolu.exists():
            zf.write(db_yolu, "efeai.db")

        # Ayarlar
        ayar_yolu = BASE_DIR / "settings.json"
        if ayar_yolu.exists():
            zf.write(ayar_yolu, "settings.json")

        # Bilgi tabanı
        veri_dizini = BASE_DIR / "knowledge_base" / "data"
        for dosya in veri_dizini.glob("*.json"):
            zf.write(dosya, f"knowledge_base/{dosya.name}")

    print(f"\n  ✓ Yedek oluşturuldu: {yedek_yolu}")
    return str(yedek_yolu)


def _kod_analiz_modu():
    """Kullanıcıdan kod alır ve analiz eder."""
    from code_engine.analyzer import kodu_analiz_et, analiz_raporu_formatla

    print(f"\n{r('── KOD ANALİZİ ──', Renk.SARI)}")
    print("  Kodu yapıştır (bitirmek için 'BITTI' yazan boş satır gir):\n")

    satirlar = []
    while True:
        satir = input()
        if satir.strip().upper() == "BITTI":
            break
        satirlar.append(satir)

    if not satirlar:
        print("  Kod girilmedi.")
        return

    kod = "\n".join(satirlar)
    analiz = kodu_analiz_et(kod)
    print("\n" + analiz_raporu_formatla(analiz))


def _gecmis_goster():
    """Son konuşma geçmişini gösterir."""
    from database import db
    from core.brain import Brain

    oturumlar = db.tum_oturumlar()
    if not oturumlar:
        print("  Geçmiş konuşma bulunamadı.")
        return

    print(f"\n  Son {min(5, len(oturumlar))} oturum:")
    for o in oturumlar[:5]:
        print(f"  [{o['session_id']}] {o['started'][:16]} — {o['msg_count']} mesaj")

    session = input("\n  Oturum ID (tam): ").strip()
    if session:
        gecmis = db.konusma_gecmisi_al(session, limit=30)
        print()
        for mesaj in gecmis:
            gonderici = "Sen   " if mesaj["role"] == "user" else "EFEAI "
            renk = Renk.CYAN if mesaj["role"] == "user" else Renk.MAVI
            print(r(f"{gonderici}›", renk), mesaj["message"][:120])


def _ana_menu(brain):
    """Ana menüyü gösterir ve seçim alır."""
    print(f"\n{r('── ANA MENÜ ──', Renk.SARI)}")
    print("  1. Yapay Zekâ ile Konuş")
    print("  2. Proje Yöneticisi")
    print("  3. Academy (Öğrenme)")
    print("  4. Kişisel Notlar")
    print("  5. Kod Analizi")
    print("  6. Konuşma Geçmişi")
    print("  7. Yedek Oluştur")
    print("  8. İstatistikler")
    print("  0. Çıkış")

    return input("\n  Seçim: ").strip()


# ─── Ana Konuşma Döngüsü ──────────────────────────────────────

def konusma_dongusu(brain):
    """Ana yapay zekâ konuşma döngüsü."""
    print(f"\n{r(brain.karakter.selamlama(), Renk.MAVI)}")
    print(r("  ('menu' yazarak menüye dön, 'çıkış' ile bitir)", Renk.GRI))
    print()

    while True:
        try:
            girdi = input(_kullanici_prompt().replace("\033[36m", "").replace("\033[0m", "")).strip()

            if not girdi:
                continue

            if girdi.lower() in ("menu", "menü"):
                break

            if girdi.lower() in ("çıkış", "cikis", "exit", "quit", "q"):
                print(_efeai_header().replace("\033[34m\033[1m", "").replace("\033[0m", "") +
                      brain.karakter.veda())
                sys.exit(0)

            # Yanıt al ve yazdır
            yanit = brain.yanit_uret(girdi)
            print()
            _formatlı_yazdir(yanit, girinti=2)

        except KeyboardInterrupt:
            print("\n\n  (Ctrl+C alındı. Menüye dönülüyor...)")
            break
        except EOFError:
            break


# ─── Giriş Noktası ────────────────────────────────────────────

def main():
    # Banner
    print(BANNER)
    print(r("  Sistem başlatılıyor...", Renk.GRI))

    try:
        brain = _sistemi_baslat()
        print(r("  ✓ Veritabanı hazır", Renk.YESIL))
        print(r("  ✓ Bilgi tabanı yüklendi", Renk.YESIL))
        print(r("  ✓ EFEAI hazır\n", Renk.YESIL))
    except Exception as e:
        print(f"\n  [HATA] Sistem başlatılamadı: {e}")
        sys.exit(1)

    # Ana döngü
    while True:
        try:
            secim = _ana_menu(brain)

            if secim == "0":
                print("\n" + brain.karakter.veda())
                break
            elif secim == "1":
                konusma_dongusu(brain)
            elif secim == "2":
                _proje_menusu()
            elif secim == "3":
                _akademi_menusu()
            elif secim == "4":
                _notlar_menusu()
            elif secim == "5":
                _kod_analiz_modu()
            elif secim == "6":
                _gecmis_goster()
            elif secim == "7":
                _yedek_olustur()
            elif secim == "8":
                from database import db
                stats = db.genel_istatistikler()
                print("\n  ═══ İSTATİSTİKLER ═══")
                for k, v in stats.items():
                    print(f"  {k:<25}: {v}")
            else:
                print("  Geçersiz seçim.")

        except KeyboardInterrupt:
            print("\n\n  Çıkmak için 0'a basın.")
        except Exception as e:
            print(f"\n  [HATA] {e}")


if __name__ == "__main__":
    main()
