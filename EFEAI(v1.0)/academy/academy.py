"""
EFEAI Academy — Öğrenme Sistemi
Kullanıcının teknoloji bilgisini sistematik olarak geliştirmesini sağlar.
Quiz soruları, öğrenme haritası, tekrar sistemi.
"""

import random
from database import db
from knowledge_base import searcher


# ─── Öğrenme Yolu ─────────────────────────────────────────────

OGRENME_YOLU = [
    {"sira": 1,  "konu": "Bilgisayar Temelleri",    "zorluk": "Başlangıç", "sure_dk": 60},
    {"sira": 2,  "konu": "Programlama Mantığı",     "zorluk": "Başlangıç", "sure_dk": 90},
    {"sira": 3,  "konu": "Algoritmalar",             "zorluk": "Başlangıç", "sure_dk": 120},
    {"sira": 4,  "konu": "Veri Yapıları",            "zorluk": "Orta",      "sure_dk": 150},
    {"sira": 5,  "konu": "Python",                   "zorluk": "Başlangıç", "sure_dk": 300},
    {"sira": 6,  "konu": "Git",                      "zorluk": "Başlangıç", "sure_dk": 60},
    {"sira": 7,  "konu": "SQL",                      "zorluk": "Başlangıç", "sure_dk": 120},
    {"sira": 8,  "konu": "HTML",                     "zorluk": "Başlangıç", "sure_dk": 90},
    {"sira": 9,  "konu": "CSS",                      "zorluk": "Başlangıç", "sure_dk": 120},
    {"sira": 10, "konu": "JavaScript",               "zorluk": "Orta",      "sure_dk": 240},
    {"sira": 11, "konu": "API Teknolojileri",        "zorluk": "Orta",      "sure_dk": 120},
    {"sira": 12, "konu": "Framework'ler",            "zorluk": "Orta",      "sure_dk": 180},
    {"sira": 13, "konu": "Mobil Geliştirme",         "zorluk": "Orta",      "sure_dk": 240},
    {"sira": 14, "konu": "Yapay Zekâ",               "zorluk": "İleri",     "sure_dk": 300},
    {"sira": 15, "konu": "İleri Yazılım Mimarileri", "zorluk": "İleri",     "sure_dk": 240},
]


# ─── Quiz Soruları ─────────────────────────────────────────────

QUIZ_SORULARI = {
    "HTML": [
        {
            "soru": "Aşağıdakilerden hangisi HTML'de doğru bir paragraf etiketidir?",
            "secenekler": ["A) <paragraph>", "B) <p>", "C) <para>", "D) <txt>"],
            "dogru": "B",
            "aciklama": "<p> etiketi HTML'de paragraf oluşturmak için kullanılır."
        },
        {
            "soru": "HTML'de bir görsel eklemek için hangi etiket kullanılır?",
            "secenekler": ["A) <picture>", "B) <image>", "C) <img>", "D) <photo>"],
            "dogru": "C",
            "aciklama": "<img src='...' alt='...'> sözdizimi ile görsel eklenir."
        },
        {
            "soru": "<!DOCTYPE html> bildirimi ne amaçla kullanılır?",
            "secenekler": [
                "A) Yorumu göstermek için",
                "B) Tarayıcıya belgenin HTML5 olduğunu bildirmek için",
                "C) Stil eklemek için",
                "D) JavaScript çalıştırmak için"
            ],
            "dogru": "B",
            "aciklama": "DOCTYPE bildirimi tarayıcıya HTML versiyonunu belirtir."
        },
        {
            "soru": "Sırasız liste oluşturmak için hangi etiket kullanılır?",
            "secenekler": ["A) <ol>", "B) <list>", "C) <ul>", "D) <li>"],
            "dogru": "C",
            "aciklama": "<ul> (unordered list) madde işaretli liste oluşturur."
        },
        {
            "soru": "HTML'de yorum satırı nasıl yazılır?",
            "secenekler": [
                "A) // Bu bir yorumdur",
                "B) # Bu bir yorumdur",
                "C) <!-- Bu bir yorumdur -->",
                "D) /* Bu bir yorumdur */"
            ],
            "dogru": "C",
            "aciklama": "HTML yorumları <!-- ve --> arasına yazılır."
        },
        {
            "soru": "Bağlantı (link) oluşturmak için hangi etiket kullanılır?",
            "secenekler": ["A) <link>", "B) <href>", "C) <url>", "D) <a>"],
            "dogru": "D",
            "aciklama": "<a href='URL'>Metin</a> sözdizimi ile bağlantı oluşturulur."
        },
        {
            "soru": "Formda metin alanı oluşturmak için hangi etiket kullanılır?",
            "secenekler": ["A) <input>", "B) <textfield>", "C) <textarea>", "D) <field>"],
            "dogru": "C",
            "aciklama": "<textarea> çok satırlı metin girişi için kullanılır."
        },
        {
            "soru": "Hangi meta etiketi Türkçe karakterlerin doğru görünmesini sağlar?",
            "secenekler": [
                "A) <meta lang='tr'>",
                "B) <meta charset='UTF-8'>",
                "C) <meta encoding='tr'>",
                "D) <meta language='turkish'>"
            ],
            "dogru": "B",
            "aciklama": "charset='UTF-8' Türkçe ve tüm Unicode karakterleri destekler."
        },
        {
            "soru": "Semantik HTML'de sayfa navigasyonu için hangi etiket uygundur?",
            "secenekler": ["A) <div class='menu'>", "B) <menu>", "C) <nav>", "D) <navigation>"],
            "dogru": "C",
            "aciklama": "<nav> semantik navigasyon etiketi olup tarayıcılara ve ekran okuyuculara anlam taşır."
        },
        {
            "soru": "img etiketinde 'alt' özniteliği ne işe yarar?",
            "secenekler": [
                "A) Görseli hizalar",
                "B) Görsel yüklenemediğinde gösterilecek alternatif metni belirler",
                "C) Görselin boyutunu ayarlar",
                "D) Görsele başlık ekler"
            ],
            "dogru": "B",
            "aciklama": "alt özniteliği erişilebilirlik ve SEO için zorunludur."
        },
    ],
    "Python": [
        {
            "soru": "Python'da bir liste nasıl tanımlanır?",
            "secenekler": ["A) liste = (1, 2, 3)", "B) liste = [1, 2, 3]", "C) liste = {1, 2, 3}", "D) liste = <1, 2, 3>"],
            "dogru": "B",
            "aciklama": "Listeler köşeli parantez [] ile tanımlanır."
        },
        {
            "soru": "Python'da bir fonksiyon nasıl tanımlanır?",
            "secenekler": ["A) function isim():", "B) func isim():", "C) def isim():", "D) define isim():"],
            "dogru": "C",
            "aciklama": "def anahtar kelimesi Python'da fonksiyon tanımlamak için kullanılır."
        },
        {
            "soru": "range(5) ifadesi hangi sayıları üretir?",
            "secenekler": ["A) 1-5", "B) 0-5", "C) 0-4", "D) 1-4"],
            "dogru": "C",
            "aciklama": "range(5) sıfırdan başlar ve 5 dahil değil; 0, 1, 2, 3, 4 üretir."
        },
        {
            "soru": "Python'da dictionary (sözlük) nasıl tanımlanır?",
            "secenekler": ["A) d = [anahtar: değer]", "B) d = (anahtar: değer)", "C) d = {anahtar: değer}", "D) d = <anahtar: değer>"],
            "dogru": "C",
            "aciklama": "Sözlükler süslü parantez {} ve iki nokta üst üste : ile tanımlanır."
        },
    ],
    "Git": [
        {
            "soru": "Git'te değişiklikleri kaydetmek için hangi komut kullanılır?",
            "secenekler": ["A) git save", "B) git commit", "C) git push", "D) git store"],
            "dogru": "B",
            "aciklama": "git commit -m 'mesaj' komutu değişiklikleri geçmişe kaydeder."
        },
        {
            "soru": "Yeni bir Git deposu başlatmak için hangi komut kullanılır?",
            "secenekler": ["A) git start", "B) git new", "C) git init", "D) git begin"],
            "dogru": "C",
            "aciklama": "git init komutu bulunduğun dizinde yeni bir Git deposu oluşturur."
        },
        {
            "soru": "Uzak depoya değişiklikleri göndermek için hangi komut kullanılır?",
            "secenekler": ["A) git send", "B) git push", "C) git upload", "D) git commit"],
            "dogru": "B",
            "aciklama": "git push origin main komutu değişiklikleri uzak depoya gönderir."
        },
    ],
}


def ogrenme_haritasi_goster() -> str:
    """Kullanıcının öğrenme haritasını görsel olarak gösterir."""
    ilerleme = db.ogrenme_haritasi()
    ilerleme_dict = {(r["topic"], r["subtopic"]): r for r in ilerleme}

    satirlar = ["═══ ÖĞRENME HARİTASI ═══\n"]

    for adim in OGRENME_YOLU:
        konu = adim["konu"]
        zorluk = adim["zorluk"]
        sure = adim["sure_dk"]
        sure_saat = f"{sure // 60}s {sure % 60}dk" if sure >= 60 else f"{sure}dk"

        kayit = ilerleme_dict.get((konu, ""), None)
        durum = kayit["status"] if kayit else "Okunmadı"

        durum_semboller = {
            "Okunmadı":    "○",
            "İncelendi":   "◔",
            "Öğreniliyor": "◑",
            "Tamamlandı":  "●",
        }
        sembol = durum_semboller.get(durum, "○")

        satirlar.append(f"  {adim['sira']:>2}. {sembol} {konu:<28} [{zorluk:<10}] ~{sure_saat}")

    satirlar.append("\n  Semboller: ○ Başlanmadı  ◔ İncelendi  ◑ Öğreniliyor  ● Tamamlandı")
    return "\n".join(satirlar)


def quiz_baslat(konu: str) -> list:
    """Belirli bir konu için quiz soruları döner."""
    sorular = QUIZ_SORULARI.get(konu, [])
    if not sorular:
        return []
    return random.sample(sorular, min(5, len(sorular)))


def quiz_yap(konu: str) -> str:
    """Interaktif quiz oturumu için metin formatı döner."""
    sorular = quiz_baslat(konu)
    if not sorular:
        return f"'{konu}' konusu için henüz quiz sorusu eklenmemiş."

    satirlar = [f"═══ {konu.upper()} QUIZ ═══", f"Toplam {len(sorular)} soru\n"]
    for i, s in enumerate(sorular, 1):
        satirlar.append(f"Soru {i}: {s['soru']}")
        for secenek in s["secenekler"]:
            satirlar.append(f"  {secenek}")
        satirlar.append(f"  → Cevap: {s['dogru']}  |  {s['aciklama']}\n")

    return "\n".join(satirlar)


def gunluk_plan_olustur(dk_musait: int = 50) -> str:
    """Günlük çalışma planı oluşturur."""
    tekrar = db.tekrar_gerekli()
    ilerleme = db.ogrenme_haritasi()

    baslangic_konular = [
        adim for adim in OGRENME_YOLU
        if adim["zorluk"] == "Başlangıç"
    ]

    kalan_dk = dk_musait
    plan = []

    # Önce tekrar gerektiren konular
    if tekrar:
        for t in tekrar[:2]:
            if kalan_dk >= 10:
                plan.append({
                    "tip": "tekrar",
                    "konu": t["topic"],
                    "sure_dk": 10,
                    "aciklama": "Tekrar zamanı geldi"
                })
                kalan_dk -= 10

    # Yeni konu öğrenme
    ilerleme_konular = {r["topic"] for r in ilerleme}
    for adim in baslangic_konular:
        if konu not in ilerleme_konular and kalan_dk >= 20:
            sure = min(adim["sure_dk"], kalan_dk // 2, 30)
            plan.append({
                "tip": "yeni",
                "konu": adim["konu"],
                "sure_dk": sure,
                "aciklama": "Yeni konu"
            })
            kalan_dk -= sure
            if kalan_dk < 20:
                break

    if kalan_dk >= 10:
        plan.append({
            "tip": "pratik",
            "konu": "Kod Pratiği",
            "sure_dk": kalan_dk,
            "aciklama": "Küçük bir proje veya egzersiz"
        })

    if not plan:
        return "Bugün için plan oluşturulamadı. Mevcut konuları tekrar etmeyi dene."

    satirlar = ["═══ GÜNLÜK ÇALIŞMA PLANI ═══"]
    toplam = 0
    for item in plan:
        sembol = "🔄" if item["tip"] == "tekrar" else ("🆕" if item["tip"] == "yeni" else "💻")
        satirlar.append(f"  {sembol} {item['konu']:<28} {item['sure_dk']:>3} dakika  — {item['aciklama']}")
        toplam += item["sure_dk"]
    satirlar.append(f"\n  Toplam: ~{toplam} dakika")

    return "\n".join(satirlar)


def konu_tamamla(konu: str, sure_dk: int = 0):
    """Bir konuyu tamamlandı olarak işaretler."""
    db.ogrenme_ilerlemesi_kaydet(konu, durum="Tamamlandı", sure_dk=sure_dk)


def konu_incele(konu: str, sure_dk: int = 0):
    """Bir konuyu incelendi olarak işaretler."""
    db.ogrenme_ilerlemesi_kaydet(konu, durum="İncelendi", sure_dk=sure_dk)


def istatistikler() -> str:
    """Öğrenme istatistiklerini döner."""
    genel = db.genel_istatistikler()
    ilerleme = db.ogrenme_haritasi()

    durum_sayilari = {}
    for r in ilerleme:
        d = r["status"]
        durum_sayilari[d] = durum_sayilari.get(d, 0) + 1

    toplam_sure = genel.get("toplam_calisma_dk", 0)
    saat = toplam_sure // 60
    dk = toplam_sure % 60

    satirlar = [
        "═══ ÖĞRENME İSTATİSTİKLERİ ═══",
        f"Çalışılan Konu  : {genel['calisilan_konu']}",
        f"Tamamlanan Konu : {genel['tamamlanan_konu']}",
        f"Toplam Süre     : {saat} saat {dk} dakika",
        f"Toplam Mesaj    : {genel['toplam_mesaj']}",
        "",
        "Durum Dağılımı:",
    ]
    for durum, adet in durum_sayilari.items():
        satirlar.append(f"  {durum:<15}: {adet}")

    return "\n".join(satirlar)
