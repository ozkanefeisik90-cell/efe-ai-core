"""
EFEAI Kod Üretici
İstek metnine göre şablon tabanlı kod üretir.
"""

import re
from typing import Optional


SABLONLAR = {
    "python": {
        "fonksiyon": '''\
def {isim}({parametreler}):
    """
    {aciklama}
    """
    # TODO: Uygulamayı buraya yaz
    pass
''',
        "sinif": '''\
class {isim}:
    """
    {aciklama}
    """

    def __init__(self{init_params}):
        {init_body}

    def __str__(self):
        return f"{isim}()"
''',
        "liste_dongusu": '''\
# Liste üzerinde döngü
ogeler = {liste}
for oge in ogeler:
    print(oge)
''',
        "dosya_oku": '''\
# Dosya okuma
with open("{dosya_yolu}", "r", encoding="utf-8") as f:
    icerik = f.read()
print(icerik)
''',
        "dosya_yaz": '''\
# Dosya yazma
with open("{dosya_yolu}", "w", encoding="utf-8") as f:
    f.write("{icerik}")
''',
        "try_except": '''\
try:
    # Riskli işlem
    sonuc = {islem}
except {hata_turu} as e:
    print(f"Hata oluştu: {e}")
except Exception as e:
    print(f"Beklenmeyen hata: {e}")
finally:
    print("İşlem tamamlandı.")
''',
        "api_istegi": '''\
import urllib.request
import json

def api_iste(url: str) -> dict:
    """API isteği gönderir ve JSON yanıtı döner."""
    with urllib.request.urlopen(url) as response:
        veri = json.loads(response.read().decode())
    return veri

sonuc = api_iste("{url}")
print(sonuc)
''',
        "sqlite": '''\
import sqlite3

# Veritabanı bağlantısı
conn = sqlite3.connect("{veritabani}.db")
cursor = conn.cursor()

# Tablo oluştur
cursor.execute("""
    CREATE TABLE IF NOT EXISTS {tablo} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isim TEXT NOT NULL,
        olusturulma TEXT DEFAULT (datetime('now'))
    )
""")

# Veri ekle
cursor.execute("INSERT INTO {tablo} (isim) VALUES (?)", ("Örnek",))
conn.commit()

# Veri oku
for satir in cursor.execute("SELECT * FROM {tablo}"):
    print(satir)

conn.close()
''',
    },
    "javascript": {
        "fonksiyon": '''\
/**
 * {aciklama}
 * @param {{{tip}}} {parametre} - Parametre açıklaması
 * @returns {{{donus_turu}}} Dönüş değeri açıklaması
 */
function {isim}({parametre}) {{
    // TODO: Uygulamayı buraya yaz
    return null;
}}
''',
        "arrow": '''\
// Ok fonksiyonu
const {isim} = ({parametre}) => {{
    return {donusumu};
}};

// Kısa form (tek satır)
const {isim}Kisa = ({parametre}) => {donusumu};
''',
        "fetch": '''\
// Fetch API ile veri çekme
async function veriCek(url) {{
    try {{
        const yanit = await fetch(url);
        if (!yanit.ok) {{
            throw new Error(`HTTP Hatası: ${{yanit.status}}`);
        }}
        const veri = await yanit.json();
        return veri;
    }} catch (hata) {{
        console.error("Hata:", hata.message);
        return null;
    }}
}}

// Kullanım
veriCek("{url}").then(veri => console.log(veri));
''',
        "sinif": '''\
class {isim} {{
    constructor({parametreler}) {{
        {init_body}
    }}

    {metot}() {{
        // Metot uygulaması
    }}

    toString() {{
        return `{isim}()`;
    }}
}}

// Kullanım
const nesne = new {isim}({ornek_degerler});
''',
    },
    "html": {
        "sayfa": '''\
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{baslik}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
    </style>
</head>
<body>
    <h1>{baslik}</h1>
    <p>{icerik}</p>

    <script>
        // JavaScript buraya
    </script>
</body>
</html>
''',
        "form": '''\
<form action="{aksiyon}" method="{metot}">
    <div>
        <label for="isim">Ad Soyad:</label>
        <input type="text" id="isim" name="isim" required>
    </div>
    <div>
        <label for="eposta">E-posta:</label>
        <input type="email" id="eposta" name="eposta" required>
    </div>
    <button type="submit">Gönder</button>
</form>
''',
        "tablo": '''\
<table>
    <thead>
        <tr>
            <th>Başlık 1</th>
            <th>Başlık 2</th>
            <th>Başlık 3</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Hücre 1</td>
            <td>Hücre 2</td>
            <td>Hücre 3</td>
        </tr>
    </tbody>
</table>
''',
    },
    "css": {
        "flexbox": '''\
/* Flexbox Düzeni */
.konteyner {{
    display: flex;
    justify-content: center;  /* Yatay hizalama */
    align-items: center;       /* Dikey hizalama */
    flex-wrap: wrap;           /* Satır kırma */
    gap: 16px;
}}

.eleman {{
    flex: 1;
    min-width: 200px;
    padding: 16px;
}}
''',
        "grid": '''\
/* CSS Grid Düzeni */
.grid-konteyner {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto;
    gap: 16px;
}}

@media (max-width: 768px) {{
    .grid-konteyner {{
        grid-template-columns: 1fr;
    }}
}}
''',
    },
    "sql": {
        "temel": '''\
-- {aciklama}
CREATE TABLE IF NOT EXISTS {tablo} (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    isim    TEXT    NOT NULL,
    tarih   TEXT    DEFAULT (datetime('now'))
);

-- Veri ekle
INSERT INTO {tablo} (isim) VALUES ('{ornek_deger}');

-- Veri sorgula
SELECT * FROM {tablo} WHERE isim = '{ornek_deger}';

-- Veri güncelle
UPDATE {tablo} SET isim = 'Yeni Değer' WHERE id = 1;

-- Veri sil
DELETE FROM {tablo} WHERE id = 1;
''',
    },
}


class KodUretici:
    """
    İstek metnini analiz ederek uygun şablon seçer ve doldurur.
    """

    def uret(self, istek: str, dil: str = "python") -> str:
        """İstek metnine göre kod üretir."""
        dil = dil.lower()
        istek_lower = istek.lower()

        # Şablon seç
        sablon_adi = self._sablon_sec(istek_lower, dil)
        sablon = SABLONLAR.get(dil, {}).get(sablon_adi)

        if not sablon:
            return self._genel_uret(istek, dil)

        # Şablonu doldur
        return self._sablon_doldur(sablon, istek, dil)

    def _sablon_sec(self, istek: str, dil: str) -> str:
        """İstekten en uygun şablonu seçer."""
        if dil == "python":
            if any(k in istek for k in ["fonksiyon", "def ", "function"]):
                return "fonksiyon"
            elif any(k in istek for k in ["class", "sınıf", "nesne"]):
                return "sinif"
            elif any(k in istek for k in ["döngü", "loop", "for", "while"]):
                return "liste_dongusu"
            elif any(k in istek for k in ["dosya oku", "file read", "open"]):
                return "dosya_oku"
            elif any(k in istek for k in ["hata yakala", "try except", "exception"]):
                return "try_except"
            elif any(k in istek for k in ["api", "request", "http", "fetch"]):
                return "api_istegi"
            elif any(k in istek for k in ["sqlite", "veritabanı", "database"]):
                return "sqlite"
        elif dil == "javascript":
            if any(k in istek for k in ["fetch", "api", "http"]):
                return "fetch"
            elif any(k in istek for k in ["class", "sınıf"]):
                return "sinif"
            elif any(k in istek for k in ["arrow", "ok fonksiyon"]):
                return "arrow"
            elif any(k in istek for k in ["fonksiyon", "function"]):
                return "fonksiyon"
        elif dil == "html":
            if any(k in istek for k in ["form", "input"]):
                return "form"
            elif any(k in istek for k in ["tablo", "table"]):
                return "tablo"
            else:
                return "sayfa"
        elif dil == "css":
            if any(k in istek for k in ["grid"]):
                return "grid"
            else:
                return "flexbox"
        elif dil == "sql":
            return "temel"
        return "fonksiyon"

    def _sablon_doldur(self, sablon: str, istek: str, dil: str) -> str:
        """Şablondaki yer tutucuları doldurur."""
        # İsimler
        istek_words = istek.split()
        isim = "benim_fonksiyon"
        for w in istek_words:
            if w.isidentifier() and len(w) > 2:
                isim = w.lower().replace(" ", "_")
                break

        sablon = sablon.replace("{isim}", isim)
        sablon = sablon.replace("{aciklama}", istek[:80])
        sablon = sablon.replace("{parametreler}", "parametre")
        sablon = sablon.replace("{parametre}", "parametre")
        sablon = sablon.replace("{init_params}", ", isim=''")
        sablon = sablon.replace("{init_body}", "self.isim = isim")
        sablon = sablon.replace("{metot}", "isle")
        sablon = sablon.replace("{donus_turu}", "any")
        sablon = sablon.replace("{tip}", "any")
        sablon = sablon.replace("{donusumu}", "parametre")
        sablon = sablon.replace("{ornek_degerler}", "")
        sablon = sablon.replace("{url}", "https://api.ornek.com/veri")
        sablon = sablon.replace("{veritabani}", "efeai")
        sablon = sablon.replace("{tablo}", "kayitlar")
        sablon = sablon.replace("{islem}", "int(input('Sayı girin: '))")
        sablon = sablon.replace("{hata_turu}", "ValueError")
        sablon = sablon.replace("{dosya_yolu}", "dosya.txt")
        sablon = sablon.replace("{icerik}", "Merhaba Dünya")
        sablon = sablon.replace("{liste}", "[1, 2, 3, 4, 5]")
        sablon = sablon.replace("{aksiyon}", "/gonder")
        sablon = sablon.replace("{metot}", "POST")
        sablon = sablon.replace("{baslik}", "EFEAI Sayfası")
        sablon = sablon.replace("{ornek_deger}", "Örnek Değer")
        return sablon

    def _genel_uret(self, istek: str, dil: str) -> str:
        """Şablon bulunamazsa genel bir yorum ve iskelet üretir."""
        yorumlar = {
            "python": "#",
            "javascript": "//",
            "java": "//",
            "html": "<!--",
            "css": "/*",
            "sql": "--",
        }
        yorum = yorumlar.get(dil, "#")
        return (
            f"{yorum} {istek}\n"
            f"{yorum} Bu konu için otomatik kod üretilemiyor.\n"
            f"{yorum} Lütfen hangi dil ve işlemi istediğini belirt.\n"
        )

    def desteklenen_diller(self) -> list:
        return list(SABLONLAR.keys())
