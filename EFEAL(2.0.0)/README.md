# EFEAI — Kişisel Teknoloji Yapay Zekâ Sistemi

> "Bilgi güçtür, anlaşılan bilgi ise ustalıktır."

EFEAI, tamamen çevrimdışı çalışan, Python ile geliştirilmiş kişisel bir teknoloji asistanıdır. Yazılım öğrenmek, kod analiz etmek, projelerini yönetmek ve teknoloji sorularına cevap bulmak için tasarlanmıştır.

---

## 🚀 Hızlı Başlangıç

```bash
# Python 3.8+ gereklidir
python main.py
```

Harici bağımlılık yoktur. Standart Python kütüphaneleri yeterlidir.

---

## 🏗️ Proje Yapısı

```
EFEAI/
├── core/                     # Ana Beyin
│   ├── brain.py              # Merkezi karar motoru
│   ├── character.py          # Konuşma kişiliği (karakter motoru)
│   ├── memory.py             # Kısa ve uzun vadeli hafıza
│   ├── intent.py             # Niyet tanıma motoru
│   ├── response.py           # Yanıt oluşturucu
│   ├── tools.py              # Araç koordinatörü
│   └── settings.py           # Ayarlar yöneticisi
│
├── code_engine/              # Kod Motoru
│   ├── analyzer.py           # Kod analizi
│   ├── generator.py          # Kod üretimi
│   ├── debugger.py           # Hata ayıklama
│   ├── formatter.py          # Kod biçimlendirme
│   └── security.py           # Güvenlik taraması
│
├── knowledge_base/           # Bilgi Tabanı
│   ├── html/                 # HTML konuları
│   ├── css/                  # CSS, Flexbox, Grid
│   ├── javascript/           # JavaScript konuları
│   ├── python/               # Python konuları
│   ├── java/                 # Java konuları
│   ├── sql/                  # SQL ve veritabanı
│   ├── git/                  # Git versiyon kontrolü
│   ├── linux/                # Linux ve terminal
│   ├── flutter/              # Flutter ve Dart
│   ├── ai/                   # Yapay Zekâ temelleri
│   ├── algorithms/           # Algoritmalar
│   ├── cybersecurity/        # Siber güvenlik
│   └── searcher.py           # Arama motoru
│
├── academy/                  # Akademi Modülü
│   ├── academy.py            # Öğrenme motoru
│   ├── lessons/              # Ders içerikleri
│   ├── quizzes/              # Quiz soruları
│   └── roadmap/              # Öğrenme yol haritaları
│
├── database/                 # Veritabanı
│   ├── db.py                 # SQLite işlemleri
│   ├── models.py             # Veri modelleri
│   └── efeai.db              # Veritabanı dosyası
│
├── workspace_module/         # Proje Yönetimi
│   ├── project_manager.py    # Proje takibi
│   ├── file_manager.py       # Dosya yönetimi
│   ├── templates.py          # Proje şablonları
│   └── exporter.py           # Veri dışa aktarma
│
├── tests/                    # Testler
│   ├── test_brain.py
│   ├── test_database.py
│   ├── test_code_engine.py
│   └── calistir_testler.py   # Tüm testleri çalıştır
│
├── logs/                     # Log dosyaları
├── backup/                   # Yedekler
├── assets/                   # Görseller ve temalar
│
├── main.py                   # Ana giriş noktası
├── settings.json             # Uygulama ayarları
├── requirements.txt          # Bağımlılıklar (yok)
└── README.md                 # Bu dosya
```

---

## ✨ Özellikler

### 🧠 Karakter Motoru
- **3 Konuşma Modu**: Normal, Samimi, Profesyonel
- **Doğal Hitap**: "Dostum" her cümlede değil, akıllıca kullanılır
- **20+ Giriş Kalıbı**: Her sohbet farklı hissettiriyor
- **Öğretici Kapanışlar**: "Bu kodu anlamana tavsiye ederim..."
- **Nazik Hata Bildirimi**: "Şurada küçük bir hata görüyorum..."

### 💡 Bilgi Tabanı (12 Teknoloji)
Her teknoloji için ayrı JSON dosyaları:

| Teknoloji | Konular |
|-----------|---------|
| HTML      | Etiketler, Formlar, Semantik |
| CSS       | Flexbox, Grid, Animasyon |
| JavaScript| Fonksiyonlar, Async, DOM |
| Python    | Listeler, Sınıflar, Fonksiyonlar |
| Java      | OOP, Kalıtım |
| SQL       | CRUD, JOIN, Optimizasyon |
| Git       | Komutlar, Dal yönetimi |
| Linux     | Terminal, Bash |
| Flutter   | Widget, State yönetimi |
| AI/ML     | Temel kavramlar |
| Algoritmalar | Sıralama, Arama |
| Siber Güvenlik | Güvenlik pratikleri |

### 🔧 Kod Motoru
- **Otomatik Dil Tespiti** (7 dil)
- **Güvenlik Taraması** (SQL Injection, XSS, eval, hardcoded key...)
- **Hata Tespiti** ile açıklamalı çözüm önerileri
- **Kod Üretici** — istek tabanlı şablon kodu
- **Kod Biçimlendirici** — Python, HTML, SQL

### 📚 Akademi
- Yapılandırılmış dersler ve quiz'ler
- Öğrenme yol haritaları (Web, Python)
- İlerleme takibi

### 🗂️ Proje Yöneticisi
- Proje oluşturma ve durum takibi
- Görev listesi (öncelikli)
- İlerleme çubuğu

---

## ⌨️ Temel Kullanım

```
> Python nedir?
> HTML nedir? detaylı anlat
> fonksiyon yaz Python
> bu kodu analiz et  → ardından kodu yapıştır
> proje oluştur
> mod değiştir samimi
> notlar
> istatistik
> yardım
```

---

## 🧪 Testleri Çalıştırma

```bash
python tests/calistir_testler.py
```

---

## 🔒 Gizlilik

EFEAI tamamen çevrimdışı çalışır. Hiçbir veri internete gönderilmez. Tüm veriler `database/efeai.db` dosyasında yerel olarak saklanır.

---

## 📝 Lisans

MIT License — Özgürce kullan, geliştir ve paylaş.

---

*"Kod yalnızca çalışmamalı; anlaşılmalı da."*  
**— EFEAI**
