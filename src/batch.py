"""CSV batch prediction."""
import re

import numpy as np
import pandas as pd

from . import ml, standards

MAX_ROWS = 20000


def template_csv():
    return ml.load_data().head(3).drop(columns="quality").to_csv(index=False)


def prepare(raw):
    """Normalise column names (case, spaces, underscores) and report missing columns."""
    df = raw.rename(columns={c: re.sub(r"[\s_\-.]+", " ", str(c).strip().strip('"').lower()) for c in raw.columns})
    df = df.rename(columns={k.lower(): k for k in ml.FEATURE_KEYS})
    return df, [k for k in ml.FEATURE_KEYS if k not in df.columns]


def run(bundle, df):
    X = df[ml.FEATURE_KEYS].apply(pd.to_numeric, errors="coerce")
    ok = X.notna().all(axis=1)
    skipped = int((~ok).sum())
    X = X[ok].iloc[:MAX_ROWS]
    if X.empty:
        return X, skipped
    trees = np.stack([t.predict(X.values) for t in bundle["model"].estimators_])
    score = np.clip(trees.mean(axis=0), 0, 10)
    conf = (np.abs(trees - score) <= 0.5).mean(axis=0)
    safety, note = [], []
    for s, row in zip(score, X.to_dict("records")):
        v = standards.verdict(standards.check(row), s, row)
        safety.append(v["short"])
        note.append(v["reasons"][0] if v["level"] != "safe" else "All properties within reference limits.")
    out = X.copy()
    out.insert(0, "row", X.index + 1)
    out["predicted_quality"] = score.round(2)
    out["rating"] = [ml.band_for(s)["label"] for s in score]
    out["confidence_pct"] = (conf * 100).round(0)
    out["safety"], out["safety_note"] = safety, note
    if "quality" in df.columns:
        out["actual_quality"] = pd.to_numeric(df.loc[X.index, "quality"], errors="coerce")
        out["error"] = (out["predicted_quality"] - out["actual_quality"]).round(2)
    return out.reset_index(drop=True), skipped
