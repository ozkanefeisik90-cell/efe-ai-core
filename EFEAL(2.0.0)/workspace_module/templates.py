"""
EFEAI Şablon Yöneticisi
Proje şablonları ve boilerplate kod üretir.
"""


PYTHON_CLI_SABLON = '''\
#!/usr/bin/env python3
"""
{proje_adi}
{aciklama}
"""

import argparse
import sys


def ana_program(args):
    """Ana program mantığı."""
    print(f"Merhaba, {proje_adi}!")


def arguman_ayarla():
    """Komut satırı argümanlarını ayarlar."""
    parser = argparse.ArgumentParser(
        prog="{proje_adi_lower}",
        description="{aciklama}",
    )
    parser.add_argument("--versiyon", action="version", version="0.1.0")
    return parser


def main():
    parser = arguman_ayarla()
    args = parser.parse_args()
    ana_program(args)


if __name__ == "__main__":
    main()
'''

PYTHON_WEB_SABLON = '''\
"""
{proje_adi} — Basit Web Sunucusu
Harici bağımlılık gerekmez: Python stdlib http.server
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class IsleyiciSinifi(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._html_gonder("<h1>{proje_adi}</h1><p>Hoş geldiniz!</p>")
        elif self.path == "/api/durum":
            self._json_gonder({{"durum": "calisıyor", "uygulama": "{proje_adi}"}})
        else:
            self.send_error(404)

    def _html_gonder(self, icerik: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(icerik.encode())

    def _json_gonder(self, veri: dict):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(veri).encode())

    def log_message(self, fmt, *args):
        pass  # Log çıktısını sustur


if __name__ == "__main__":
    sunucu = HTTPServer(("0.0.0.0", 8080), IsleyiciSinifi)
    print(f"{proje_adi} — http://localhost:8080 adresinde çalışıyor")
    sunucu.serve_forever()
'''

PYTHON_SINIF_SABLON = '''\
"""
{proje_adi} — Veri Modeli
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class {sinif_adi}:
    """
    {aciklama}
    """
    id: int = 0
    isim: str = ""
    aciklama: Optional[str] = None
    olusturulma: str = field(default_factory=lambda: datetime.now().isoformat())
    etiketler: List[str] = field(default_factory=list)

    def gecerli_mi(self) -> bool:
        """Nesnenin geçerli olup olmadığını kontrol eder."""
        return bool(self.isim)

    def sozluge_donustur(self) -> dict:
        """Nesneyi sözlüğe dönüştürür."""
        return {{
            "id": self.id,
            "isim": self.isim,
            "aciklama": self.aciklama,
            "olusturulma": self.olusturulma,
            "etiketler": self.etiketler,
        }}

    @classmethod
    def sozlukten_olustur(cls, veri: dict) -> "{sinif_adi}":
        """Sözlükten nesne oluşturur."""
        return cls(**{{k: v for k, v in veri.items() if k in cls.__dataclass_fields__}})

    def __str__(self) -> str:
        return f"{sinif_adi}(id={{self.id}}, isim={{self.isim!r}})"
'''

FLUTTER_EKRAN_SABLON = '''\
import 'package:flutter/material.dart';

class {ekran_adi}Ekrani extends StatefulWidget {{
  const {ekran_adi}Ekrani({{super.key}});

  @override
  State<{ekran_adi}Ekrani> createState() => _{ekran_adi}EkraniState();
}}

class _{ekran_adi}EkraniState extends State<{ekran_adi}Ekrani> {{
  @override
  void initState() {{
    super.initState();
    // Başlangıç işlemleri
  }}

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{ekran_adi}'),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
      ),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.star, size: 80),
            SizedBox(height: 16),
            Text(
              '{ekran_adi} Ekranı',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {{
          // FAB işlemi
        }},
        child: const Icon(Icons.add),
      ),
    );
  }}
}}
'''

HTML_MODERN_SABLON = '''\
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{aciklama}">
    <title>{proje_adi}</title>
    <style>
        :root {{
            --renk-birincil: #2563eb;
            --renk-arkaplan: #f8fafc;
            --renk-metin: #1e293b;
            --yaricap: 8px;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: var(--renk-arkaplan);
            color: var(--renk-metin);
            line-height: 1.6;
        }}
        header {{
            background: var(--renk-birincil);
            color: white;
            padding: 1rem 2rem;
        }}
        main {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .kart {{
            background: white;
            border-radius: var(--yaricap);
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: #64748b;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{proje_adi}</h1>
    </header>
    <main>
        <div class="kart">
            <h2>Hoş Geldiniz</h2>
            <p>{aciklama}</p>
        </div>
    </main>
    <footer>
        <p>{proje_adi} &copy; 2025</p>
    </footer>
    <script>
        // JavaScript kodu buraya
        console.log('{proje_adi} yüklendi.');
    </script>
</body>
</html>
'''

SABLONLAR = {
    "python-cli":    {"ad": "Python CLI Uygulaması", "icerik": PYTHON_CLI_SABLON,    "dosya": "main.py"},
    "python-web":    {"ad": "Python Web Sunucusu",    "icerik": PYTHON_WEB_SABLON,    "dosya": "server.py"},
    "python-sinif":  {"ad": "Python Veri Modeli",     "icerik": PYTHON_SINIF_SABLON,  "dosya": "model.py"},
    "flutter-ekran": {"ad": "Flutter Ekranı",          "icerik": FLUTTER_EKRAN_SABLON, "dosya": "ekran.dart"},
    "html-modern":   {"ad": "Modern HTML Sayfası",     "icerik": HTML_MODERN_SABLON,   "dosya": "index.html"},
}


class SablonYoneticisi:
    """Proje şablonlarını yönetir ve doldurur."""

    def listele(self) -> str:
        """Mevcut şablonları listeler."""
        satirlar = ["📑 Mevcut Proje Şablonları:", ""]
        for anahtar, sablon in SABLONLAR.items():
            satirlar.append(f"  • {anahtar:<20} — {sablon['ad']}")
        satirlar.append("\nKullanım: 'X şablonunu ver' veya 'X template'")
        return "\n".join(satirlar)

    def sablon_al(self, tur: str, degiskenler: dict = None) -> str:
        """Belirtilen şablonu döner."""
        tur = tur.lower().replace(" ", "-")
        sablon = SABLONLAR.get(tur)
        if not sablon:
            # Kısmi eşleşme
            for anahtar in SABLONLAR:
                if tur in anahtar or anahtar in tur:
                    sablon = SABLONLAR[anahtar]
                    break

        if not sablon:
            mevcut = ", ".join(SABLONLAR.keys())
            return f"Şablon bulunamadı. Mevcut şablonlar: {mevcut}"

        icerik = sablon["icerik"]
        if degiskenler:
            for k, v in degiskenler.items():
                icerik = icerik.replace(f"{{{k}}}", str(v))

        # Varsayılan değerleri doldur
        icerik = icerik.replace("{proje_adi}", degiskenler.get("proje_adi", "BenimProjem") if degiskenler else "BenimProjem")
        icerik = icerik.replace("{aciklama}", degiskenler.get("aciklama", "EFEAI ile oluşturuldu.") if degiskenler else "EFEAI ile oluşturuldu.")
        icerik = icerik.replace("{proje_adi_lower}", "benim_projem")
        icerik = icerik.replace("{sinif_adi}", "VeriModeli")
        icerik = icerik.replace("{ekran_adi}", "Ana")

        return (
            f"📄 {sablon['ad']} — {sablon['dosya']}\n"
            f"{'─' * 50}\n"
            f"{icerik}"
        )
