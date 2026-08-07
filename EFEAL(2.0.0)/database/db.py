"""
EFEAI SQLite Veritabanı — Hafıza Motoru
Konuşma geçmişi, projeler, öğrenme ilerlemesi, notlar ve favoriler.
"""

import sqlite3
import json
from datetime import datetime, date
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "efeai.db"


def baglanti_al() -> sqlite3.Connection:
    """Veritabanı bağlantısı döner."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def tablolari_olustur():
    """Tüm tabloları oluşturur."""
    with baglanti_al() as conn:
        conn.executescript("""
            -- Konuşma geçmişi
            CREATE TABLE IF NOT EXISTS conversations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL,
                role        TEXT NOT NULL CHECK(role IN ('user', 'efeai')),
                message     TEXT NOT NULL,
                topic       TEXT,
                mode        TEXT DEFAULT 'normal',
                timestamp   TEXT NOT NULL DEFAULT (datetime('now'))
            );

            -- Projeler
            CREATE TABLE IF NOT EXISTS projects (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                description     TEXT,
                language        TEXT,
                technologies    TEXT,         -- JSON array
                project_type    TEXT,
                status          TEXT DEFAULT 'Planlanıyor'
                                CHECK(status IN ('Planlanıyor','Geliştiriliyor','Test Ediliyor','Tamamlandı','Arşivlendi')),
                progress        INTEGER DEFAULT 0 CHECK(progress BETWEEN 0 AND 100),
                notes           TEXT,
                folder_path     TEXT,
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            -- Proje görevleri
            CREATE TABLE IF NOT EXISTS project_tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                title       TEXT NOT NULL,
                done        INTEGER DEFAULT 0,
                priority    TEXT DEFAULT 'normal' CHECK(priority IN ('düşük','normal','yüksek')),
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                done_at     TEXT
            );

            -- Proje günlüğü
            CREATE TABLE IF NOT EXISTS project_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                log_entry   TEXT NOT NULL,
                logged_at   TEXT NOT NULL DEFAULT (datetime('now'))
            );

            -- Öğrenme ilerlemesi
            CREATE TABLE IF NOT EXISTS learning_progress (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                topic           TEXT NOT NULL,
                subtopic        TEXT,
                status          TEXT DEFAULT 'Okunmadı'
                                CHECK(status IN ('Okunmadı','İncelendi','Öğreniliyor','Tamamlandı')),
                score           INTEGER DEFAULT 0,
                study_minutes   INTEGER DEFAULT 0,
                last_studied    TEXT,
                review_date     TEXT,
                notes           TEXT,
                UNIQUE(topic, subtopic)
            );

            -- Kişisel notlar
            CREATE TABLE IF NOT EXISTS notes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                content     TEXT NOT NULL,
                topic       TEXT,
                tags        TEXT,             -- JSON array
                is_favorite INTEGER DEFAULT 0,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );

            -- Favoriler (bilgi tabanı konuları)
            CREATE TABLE IF NOT EXISTS favorites (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                topic       TEXT NOT NULL,
                subtopic    TEXT,
                added_at    TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(topic, subtopic)
            );

            -- Günlük çalışma oturumları
            CREATE TABLE IF NOT EXISTS study_sessions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                date            TEXT NOT NULL DEFAULT (date('now')),
                duration_min    INTEGER DEFAULT 0,
                topics_studied  TEXT,         -- JSON array
                notes           TEXT
            );

            -- Uygulama logları
            CREATE TABLE IF NOT EXISTS app_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                level       TEXT DEFAULT 'info' CHECK(level IN ('info','warning','error')),
                message     TEXT NOT NULL,
                detail      TEXT,
                logged_at   TEXT NOT NULL DEFAULT (datetime('now'))
            );

            -- Quiz soruları ve yanıtları
            CREATE TABLE IF NOT EXISTS quiz_results (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                topic       TEXT NOT NULL,
                question    TEXT NOT NULL,
                user_answer TEXT,
                correct     INTEGER DEFAULT 0,
                taken_at    TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)


# ─── Konuşma Geçmişi ──────────────────────────────────────────

def konusma_kaydet(session_id: str, role: str, message: str,
                   topic: str = None, mode: str = "normal"):
    with baglanti_al() as conn:
        conn.execute(
            "INSERT INTO conversations (session_id, role, message, topic, mode) VALUES (?,?,?,?,?)",
            (session_id, role, message, topic, mode)
        )


def konusma_gecmisi_al(session_id: str, limit: int = 20) -> list:
    with baglanti_al() as conn:
        rows = conn.execute(
            "SELECT role, message, topic, timestamp FROM conversations "
            "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def tum_oturumlar() -> list:
    with baglanti_al() as conn:
        rows = conn.execute(
            "SELECT DISTINCT session_id, MIN(timestamp) as started, COUNT(*) as msg_count "
            "FROM conversations GROUP BY session_id ORDER BY started DESC"
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Projeler ─────────────────────────────────────────────────

def proje_olustur(name: str, description: str = "", language: str = "",
                  technologies: list = None, project_type: str = "") -> int:
    with baglanti_al() as conn:
        techs = json.dumps(technologies or [], ensure_ascii=False)
        cursor = conn.execute(
            "INSERT INTO projects (name, description, language, technologies, project_type) VALUES (?,?,?,?,?)",
            (name, description, language, techs, project_type)
        )
        pid = cursor.lastrowid
        proje_log_ekle(pid, f"Proje oluşturuldu: {name}")
        return pid


def proje_listele(durum: str = None) -> list:
    with baglanti_al() as conn:
        if durum:
            rows = conn.execute(
                "SELECT * FROM projects WHERE status = ? ORDER BY updated_at DESC", (durum,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC"
            ).fetchall()
    result = []
    for r in rows:
        p = dict(r)
        try:
            p["technologies"] = json.loads(p.get("technologies") or "[]")
        except Exception:
            p["technologies"] = []
        result.append(p)
    return result


def proje_al(proje_id: int) -> dict:
    with baglanti_al() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (proje_id,)).fetchone()
    if not row:
        return None
    p = dict(row)
    try:
        p["technologies"] = json.loads(p.get("technologies") or "[]")
    except Exception:
        p["technologies"] = []
    return p


def proje_guncelle(proje_id: int, **kwargs):
    izin_verilen = {"name", "description", "language", "technologies",
                    "project_type", "status", "progress", "notes"}
    guncelleme = {k: v for k, v in kwargs.items() if k in izin_verilen}
    if not guncelleme:
        return False
    if "technologies" in guncelleme and isinstance(guncelleme["technologies"], list):
        guncelleme["technologies"] = json.dumps(guncelleme["technologies"], ensure_ascii=False)
    guncelleme["updated_at"] = datetime.now().isoformat()
    kolonlar = ", ".join(f"{k} = ?" for k in guncelleme)
    degerler = list(guncelleme.values()) + [proje_id]
    with baglanti_al() as conn:
        conn.execute(f"UPDATE projects SET {kolonlar} WHERE id = ?", degerler)
        proje_log_ekle(proje_id, f"Proje güncellendi: {', '.join(guncelleme.keys())}")
    return True


def proje_sil(proje_id: int):
    with baglanti_al() as conn:
        conn.execute("DELETE FROM projects WHERE id = ?", (proje_id,))


def proje_arsivle(proje_id: int):
    proje_guncelle(proje_id, status="Arşivlendi")


# ─── Proje Görevleri ──────────────────────────────────────────

def gorev_ekle(proje_id: int, baslik: str, oncelik: str = "normal") -> int:
    with baglanti_al() as conn:
        cursor = conn.execute(
            "INSERT INTO project_tasks (project_id, title, priority) VALUES (?,?,?)",
            (proje_id, baslik, oncelik)
        )
        return cursor.lastrowid


def gorev_tamamla(gorev_id: int):
    with baglanti_al() as conn:
        conn.execute(
            "UPDATE project_tasks SET done = 1, done_at = datetime('now') WHERE id = ?",
            (gorev_id,)
        )


def proje_gorevleri(proje_id: int) -> list:
    with baglanti_al() as conn:
        rows = conn.execute(
            "SELECT * FROM project_tasks WHERE project_id = ? ORDER BY done, priority DESC",
            (proje_id,)
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Proje Günlüğü ────────────────────────────────────────────

def proje_log_ekle(proje_id: int, mesaj: str):
    with baglanti_al() as conn:
        conn.execute(
            "INSERT INTO project_logs (project_id, log_entry) VALUES (?,?)",
            (proje_id, mesaj)
        )


def proje_log_al(proje_id: int) -> list:
    with baglanti_al() as conn:
        rows = conn.execute(
            "SELECT log_entry, logged_at FROM project_logs WHERE project_id = ? ORDER BY id DESC LIMIT 20",
            (proje_id,)
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Öğrenme İlerlemesi ───────────────────────────────────────

def ogrenme_ilerlemesi_kaydet(konu: str, alt_konu: str = None,
                               durum: str = "İncelendi", sure_dk: int = 0):
    review = None
    # 1 gün sonra tekrar hatırlatma
    from datetime import timedelta
    review = (date.today() + timedelta(days=1)).isoformat()

    with baglanti_al() as conn:
        conn.execute("""
            INSERT INTO learning_progress (topic, subtopic, status, study_minutes, last_studied, review_date)
            VALUES (?,?,?,?,date('now'),?)
            ON CONFLICT(topic, subtopic) DO UPDATE SET
                status = excluded.status,
                study_minutes = study_minutes + excluded.study_minutes,
                last_studied = excluded.last_studied,
                review_date = excluded.review_date
        """, (konu, alt_konu or "", durum, sure_dk, review))


def ogrenme_haritasi() -> list:
    with baglanti_al() as conn:
        rows = conn.execute(
            "SELECT topic, subtopic, status, study_minutes, last_studied, review_date "
            "FROM learning_progress ORDER BY topic, subtopic"
        ).fetchall()
    return [dict(r) for r in rows]


def tekrar_gerekli() -> list:
    """Bugün tekrar edilmesi gereken konuları döner."""
    with baglanti_al() as conn:
        rows = conn.execute(
            "SELECT topic, subtopic, status, last_studied FROM learning_progress "
            "WHERE review_date <= date('now') ORDER BY review_date"
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Notlar ───────────────────────────────────────────────────

def not_ekle(baslik: str, icerik: str, konu: str = None,
             etiketler: list = None) -> int:
    with baglanti_al() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, content, topic, tags) VALUES (?,?,?,?)",
            (baslik, icerik, konu, json.dumps(etiketler or [], ensure_ascii=False))
        )
        return cursor.lastrowid


def not_listele(konu: str = None) -> list:
    with baglanti_al() as conn:
        if konu:
            rows = conn.execute(
                "SELECT * FROM notes WHERE topic = ? ORDER BY updated_at DESC", (konu,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()
    return [dict(r) for r in rows]


def not_guncelle(not_id: int, baslik: str = None, icerik: str = None):
    with baglanti_al() as conn:
        if baslik and icerik:
            conn.execute(
                "UPDATE notes SET title=?, content=?, updated_at=datetime('now') WHERE id=?",
                (baslik, icerik, not_id)
            )
        elif icerik:
            conn.execute(
                "UPDATE notes SET content=?, updated_at=datetime('now') WHERE id=?",
                (icerik, not_id)
            )


def not_sil(not_id: int):
    with baglanti_al() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (not_id,))


# ─── Favoriler ────────────────────────────────────────────────

def favori_ekle(konu: str, alt_konu: str = None):
    with baglanti_al() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO favorites (topic, subtopic) VALUES (?,?)",
            (konu, alt_konu or "")
        )


def favori_cikar(konu: str, alt_konu: str = None):
    with baglanti_al() as conn:
        conn.execute(
            "DELETE FROM favorites WHERE topic=? AND subtopic=?",
            (konu, alt_konu or "")
        )


def favoriler() -> list:
    with baglanti_al() as conn:
        rows = conn.execute(
            "SELECT topic, subtopic, added_at FROM favorites ORDER BY topic"
        ).fetchall()
    return [dict(r) for r in rows]


# ─── İstatistikler ────────────────────────────────────────────

def genel_istatistikler() -> dict:
    with baglanti_al() as conn:
        proje_sayisi = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        tamamlanan = conn.execute(
            "SELECT COUNT(*) FROM projects WHERE status = 'Tamamlandı'"
        ).fetchone()[0]
        not_sayisi = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        konu_sayisi = conn.execute("SELECT COUNT(*) FROM learning_progress").fetchone()[0]
        tamamlanan_konu = conn.execute(
            "SELECT COUNT(*) FROM learning_progress WHERE status = 'Tamamlandı'"
        ).fetchone()[0]
        favori_sayisi = conn.execute("SELECT COUNT(*) FROM favorites").fetchone()[0]
        toplam_sure = conn.execute(
            "SELECT COALESCE(SUM(study_minutes), 0) FROM learning_progress"
        ).fetchone()[0]
        konusma_sayisi = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]

    return {
        "proje_sayisi": proje_sayisi,
        "tamamlanan_proje": tamamlanan,
        "not_sayisi": not_sayisi,
        "calisilan_konu": konu_sayisi,
        "tamamlanan_konu": tamamlanan_konu,
        "favori_sayisi": favori_sayisi,
        "toplam_calisma_dk": toplam_sure,
        "toplam_mesaj": konusma_sayisi,
    }


# ─── Uygulama Logu ────────────────────────────────────────────

def log_ekle(mesaj: str, seviye: str = "info", detay: str = None):
    with baglanti_al() as conn:
        conn.execute(
            "INSERT INTO app_logs (level, message, detail) VALUES (?,?,?)",
            (seviye, mesaj, detay)
        )


def son_loglar(limit: int = 20) -> list:
    with baglanti_al() as conn:
        rows = conn.execute(
            "SELECT level, message, detail, logged_at FROM app_logs ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
