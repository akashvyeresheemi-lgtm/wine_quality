"""SQLite persistence for prediction history."""
import json
import sqlite3

from .ml import ROOT

DB_PATH = ROOT / "data" / "predictions.db"


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, score REAL, label TEXT,
        confidence REAL, type TEXT, version TEXT, inputs TEXT, contributions TEXT)""")
    return c


def add(rec):
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO predictions(ts,score,label,confidence,type,version,inputs,contributions) VALUES(?,?,?,?,?,?,?,?)",
            (rec["ts"], rec["score"], rec["label"], rec["confidence"], rec["type"], rec["version"],
             json.dumps(rec["values"]), json.dumps(rec["contributions"])))
        return cur.lastrowid


def _row(r):
    d = dict(r)
    d["values"] = json.loads(d.pop("inputs"))
    d["contributions"] = json.loads(d["contributions"])
    return d


def all_records(limit=None):
    q = "SELECT * FROM predictions ORDER BY id DESC" + (f" LIMIT {int(limit)}" if limit else "")
    with _conn() as c:
        return [_row(r) for r in c.execute(q)]


def get(rec_id):
    with _conn() as c:
        r = c.execute("SELECT * FROM predictions WHERE id=?", (rec_id,)).fetchone()
        return _row(r) if r else None


def clear():
    with _conn() as c:
        c.execute("DELETE FROM predictions")
