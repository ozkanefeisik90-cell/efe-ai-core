# EFEAI — Kişisel Teknoloji Yapay Zekâ Sistemi

> "Learn. Build. Improve."

Versiyon: **0.1.0** | Platform: **Python 3.8+** | Bağlantı: **Çevrimdışı** | Veritabanı: **SQLite**

---

## Özellikler

| Modül             | Açıklama                                              |
|-------------------|-------------------------------------------------------|
| 🧠 Beyin Motoru   | Sorguları analiz eder, doğru modüle yönlendirir      |
| 🎭 Karakter Motoru| Normal / Samimi / Profesyonel konuşma modları        |
| 📚 Bilgi Tabanı   | JSON tabanlı HTML bilgi kütüphanesi (genişletilebilir)|
| 🔍 Arama Motoru   | Eş anlamlı kelime + anlam ilişkisi araması            |
| 💻 Kod Analizi    | Python, HTML, JS, SQL analizi ve güvenlik kontrolü   |
| 📁 Proje Yönetimi | Proje oluşturma, görev takibi, ilerleme yönetimi     |
| 🎓 Academy        | Öğrenme haritası, quiz, günlük çalışma planı         |
| 📝 Notlar         | Kişisel not defteri                                  |
| 💾 SQLite Hafıza  | Konuşma geçmişi, projeler, öğrenme ilerlemesi        |
| 📦 Yedekleme      | Tek tıkla ZIP yedekleme                              |

---

## Kurulum

```bash
# Python 3.8 veya üstü gereklidir
python --version

# Harici bağımlılık yok — sadece çalıştır:
python main.py
```

---

## Dosya Yapısı

```
EFEAI/
├── main.py                          ← Başlangıç noktası
├── settings.json                    ← Uygulama ayarları
├── requirements.txt                 ← (Standart kütüphane, pip gerekmez)
│
├── core/
│   ├── brain.py                     ← Beyin / karar motoru
│   ├── character_engine.py          ← Karakter / kişilik motoru
│   └── settings.py                  ← Ayar yöneticisi
│
├── database/
│   ├── db.py                        ← SQLite işlemleri (hafıza)
│   └── efeai.db                     ← Otomatik oluşturulur
│
├── knowledge_base/
│   ├── searcher.py                  ← Arama motoru
│   └── data/
│       └── HTML.json                ← HTML bilgi tabanı
│
├── code_engine/
│   └── analyzer.py                  ← Kod analiz motoru
│
├── workspace_module/
│   └── project_manager.py           ← Proje yöneticisi
│
├── academy/
│   └── academy.py                   ← Öğrenme sistemi
│
├── logs/                            ← Uygulama logları
└── backup/                          ← Yedek dosyaları
```

---

## Bilgi Tabanına Yeni Konu Ekleme

`knowledge_base/data/` dizinine yeni bir JSON dosyası ekle:

```json
{
  "topic": "CSS",
  "version": "1.0",
  "difficulty": "Başlangıç",
  "tags_keywords": ["css", "stil", "tasarım"],

  "definitions": [
    {
      "id": "css_001",
      "title": "CSS Nedir?",
      "content": "CSS, HTML öğelerinin görsel stilini belirler.",
      "difficulty": "Başlangıç",
      "keywords": ["css nedir", "stil"]
    }
  ],

  "tags": [
    {
      "name": "color",
      "description": "Metin rengini belirler.",
      "example": "p { color: red; }",
      "category": "Metin",
      "self_closing": false
    }
  ],

  "examples": [
    {
      "id": "ex_001",
      "title": "Temel CSS",
      "description": "Renk ve font ayarlama.",
      "code": "body { font-family: Arial; color: #333; }"
    }
  ],

  "errors": [
    {
      "id": "err_001",
      "problem": "Noktalı virgül eksik",
      "solution": "Her CSS kuralı noktalı virgül ile bitmelidir.",
      "wrong_example": "color: red",
      "correct_example": "color: red;"
    }
  ],

  "tips": [
    "CSS sıfırlamak için normalize.css kullan.",
    "Mobil öncelikli (mobile-first) yaklaşımı benimse."
  ],

  "related_topics": ["HTML", "JavaScript"]
}
```

Sistem otomatik olarak yeni dosyayı tanır ve aramaya dahil eder.

---

## Karakter Motoru

| Mod           | Örnek                                                     |
|---------------|-----------------------------------------------------------|
| Normal        | "Şöyle açıklayayım."                                      |
| Samimi        | "Dostum, bunu birlikte inceleyelim."                      |
| Profesyonel   | "Teknik açıdan değerlendirirsek:"                         |

Mod değiştirmek için konuşmada: `mod: samimi` veya `mod: profesyonel` yaz.

---

## SQLite Tablolar

| Tablo               | İçerik                            |
|---------------------|-----------------------------------|
| `conversations`     | Tüm konuşma geçmişi               |
| `projects`          | Projeler                          |
| `project_tasks`     | Proje görevleri                   |
| `project_logs`      | Proje günlüğü                     |
| `learning_progress` | Öğrenme ilerlemesi                |
| `notes`             | Kişisel notlar                    |
| `favorites`         | Favori konular                    |
| `quiz_results`      | Quiz sonuçları                    |
| `app_logs`          | Sistem logları                    |

---

## Yol Haritası

| Sürüm  | Özellikler                              |
|--------|-----------------------------------------|
| 0.1.0  | Temel sistem (mevcut)                   |
| 0.5.0  | CSS, Python, Git bilgi tabanları        |
| 1.0.0  | Tam kararlı sürüm                       |
| 1.5.0  | Ses girişi, görsel analiz               |
| 2.0.0  | Yerel yapay zekâ modeli entegrasyonu    |

---

*EFEAI — Kod yalnızca çalışmamalı; anlaşılmalı da.*
