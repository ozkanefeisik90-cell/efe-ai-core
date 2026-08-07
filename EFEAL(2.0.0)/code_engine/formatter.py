"""
EFEAI Kod Biçimlendirici
Kodu okunabilir formata getirir, girintileri düzenler.
Harici bağımlılık yok — sadece standart kütüphane.
"""

import re
import textwrap
from typing import Optional


class KodBiçimlendirici:
    """
    Dile göre kod biçimlendirme yapar.
    """

    def bicimlendir(self, kod: str, dil: str = "python") -> str:
        """Kodu dile göre biçimlendirir."""
        dil = dil.lower()
        if dil == "python":
            return self._python_bicimlendir(kod)
        elif dil in ("javascript", "js"):
            return self._js_bicimlendir(kod)
        elif dil == "html":
            return self._html_bicimlendir(kod)
        elif dil == "sql":
            return self._sql_bicimlendir(kod)
        else:
            return self._genel_bicimlendir(kod)

    def _python_bicimlendir(self, kod: str) -> str:
        """Python kodunu temel PEP 8 kurallarına göre biçimlendirir."""
        satirlar = kod.splitlines()
        yeni_satirlar = []

        for satir in satirlar:
            # Sekmeleri 4 boşluğa çevir
            satir = satir.replace("\t", "    ")
            # Sonda gereksiz boşlukları kaldır
            satir = satir.rstrip()
            yeni_satirlar.append(satir)

        # Fazla boş satırları temizle (3+ boş → 2 boş)
        temiz = []
        bos_sayac = 0
        for satir in yeni_satirlar:
            if satir == "":
                bos_sayac += 1
                if bos_sayac <= 2:
                    temiz.append(satir)
            else:
                bos_sayac = 0
                temiz.append(satir)

        return "\n".join(temiz)

    def _js_bicimlendir(self, kod: str) -> str:
        """JavaScript kodunu temel kurallara göre biçimlendirir."""
        satirlar = kod.splitlines()
        yeni_satirlar = []

        for satir in satirlar:
            satir = satir.replace("\t", "  ")  # JS genellikle 2 boşluk
            satir = satir.rstrip()
            yeni_satirlar.append(satir)

        return "\n".join(yeni_satirlar)

    def _html_bicimlendir(self, kod: str) -> str:
        """HTML kodunu girintili biçimlendirir."""
        girintisiz = re.sub(r'>\s+<', '>\n<', kod)
        satirlar = girintisiz.splitlines()
        yeni_satirlar = []
        girinti = 0
        kapanan_etiketler = re.compile(r'^</\w+')
        acilan_etiketler = re.compile(r'^<\w+[^/]*>(?!.*</')
        kendi_kapanan = re.compile(r'<\w+[^>]*/>')

        for satir in satirlar:
            satir = satir.strip()
            if not satir:
                continue

            if kapanan_etiketler.match(satir):
                girinti = max(0, girinti - 1)

            yeni_satirlar.append("  " * girinti + satir)

            if acilan_etiketler.match(satir) and not kendi_kapanan.match(satir):
                if not satir.startswith("<!"):
                    girinti += 1

        return "\n".join(yeni_satirlar)

    def _sql_bicimlendir(self, kod: str) -> str:
        """SQL sorgusunu büyük harfe ve girintili biçimlendirir."""
        anahtar_kelimeler = [
            "SELECT", "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN",
            "INNER JOIN", "ON", "GROUP BY", "ORDER BY", "HAVING",
            "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM",
            "CREATE TABLE", "ALTER TABLE", "DROP TABLE", "INDEX",
            "AND", "OR", "NOT", "IN", "LIKE", "BETWEEN", "IS NULL",
            "IS NOT NULL", "AS", "DISTINCT", "LIMIT", "OFFSET",
        ]

        for kw in sorted(anahtar_kelimeler, key=len, reverse=True):
            kod = re.sub(
                r'\b' + re.escape(kw.lower()) + r'\b',
                kw,
                kod,
                flags=re.IGNORECASE,
            )

        return kod

    def _genel_bicimlendir(self, kod: str) -> str:
        """Genel biçimlendirme — sadece girint ve boşluk temizliği."""
        satirlar = [s.rstrip() for s in kod.splitlines()]
        return "\n".join(satirlar)

    def satir_sayisi(self, kod: str) -> int:
        """Kod satır sayısını döner."""
        return len([s for s in kod.splitlines() if s.strip()])

    def karakter_sayisi(self, kod: str) -> int:
        """Karakter sayısını döner."""
        return len(kod)

    def yorum_orani(self, kod: str, dil: str = "python") -> float:
        """Yorum satırlarının oranını döner."""
        yorum_isaretleri = {
            "python": "#",
            "javascript": "//",
            "java": "//",
            "html": "<!--",
            "css": "/*",
            "sql": "--",
        }
        isaretcı = yorum_isaretleri.get(dil, "#")
        satirlar = kod.splitlines()
        if not satirlar:
            return 0.0
        yorum_satirlar = sum(1 for s in satirlar if s.strip().startswith(isaretcı))
        return yorum_satirlar / len(satirlar)
