import sqlite3
from datetime import datetime, timezone

DB_PATH = "subrecon.db"

def init_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.execute("""CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT NOT NULL,
        scanned_at TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS findings (
        scan_id INTEGER NOT NULL REFERENCES scans(id),
        subdomain TEXT NOT NULL)""")
    conn.commit()
    return conn


def get_last_scan(conn, domain):
    row = conn.execute(
        "SELECT id FROM scans WHERE domain = ? ORDER BY id DESC LIMIT 1",
        (domain,),
    ).fetchone()
    if row is None:
        return None
    rows = conn.execute(
        "SELECT subdomain FROM findings WHERE scan_id = ?", (row[0],)
    ).fetchall()
    return {r[0] for r in rows}


def save_scan(conn, domain, subdomains):
    cur = conn.execute(
        "INSERT INTO scans (domain, scanned_at) VALUES (?, ?)",
        (domain, datetime.now(timezone.utc).isoformat()),
    )
    conn.executemany(
        "INSERT INTO findings (scan_id, subdomain) VALUES (?, ?)",
        [(cur.lastrowid, s) for s in subdomains],
    )
    conn.commit()


def diff_scans(previous, current):
    return current - previous, previous - current  # (new, gone!!)
