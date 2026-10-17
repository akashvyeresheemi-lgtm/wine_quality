"""Model loading, prediction, explanation and rule-based insights."""
import json
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "winequality-red.csv"
MODEL_PATH = ROOT / "models" / "wine_model.joblib"
METRICS_PATH = ROOT / "models" / "metrics.json"
MODEL_VERSION = "v1.0.0"


def _f(key, label, lo, hi, default, step, fmt):
    return dict(key=key, label=label, lo=lo, hi=hi, default=default, step=step, fmt=fmt)


FEATURES = [
    _f("fixed acidity", "Fixed Acidity", 0.0, 15.0, 7.4, 0.1, "%.1f"),
    _f("volatile acidity", "Volatile Acidity", 0.0, 2.0, 0.7, 0.01, "%.2f"),
    _f("citric acid", "Citric Acid", 0.0, 1.0, 0.0, 0.01, "%.2f"),
    _f("residual sugar", "Residual Sugar", 0.0, 15.0, 1.9, 0.1, "%.1f"),
    _f("chlorides", "Chlorides", 0.0, 1.0, 0.076, 0.001, "%.3f"),
    _f("free sulfur dioxide", "Free Sulfur Dioxide", 1.0, 300.0, 11.0, 1.0, "%.1f"),
    _f("total sulfur dioxide", "Total Sulfur Dioxide", 6.0, 300.0, 34.0, 1.0, "%.1f"),
    _f("density", "Density", 0.9, 1.1, 0.9978, 0.0001, "%.4f"),
    _f("pH", "pH", 2.5, 4.5, 3.51, 0.01, "%.2f"),
    _f("sulphates", "Sulphates", 0.3, 2.0, 0.56, 0.01, "%.2f"),
    _f("alcohol", "Alcohol", 8.0, 15.0, 9.4, 0.1, "%.1f"),
]
FEATURE_KEYS = [f["key"] for f in FEATURES]
LABEL_OF = {f["key"]: f["label"] for f in FEATURES}
DEFAULTS = {f["key"]: f["default"] for f in FEATURES}
RADAR_AXES = ["alcohol", "sulphates", "citric acid", "pH", "chlorides",
              "volatile acidity", "residual sugar"]

# (minimum score, label, band word, colour, explanation)
BANDS = [
    (7.0, "Excellent Quality", "excellent", "#22d39a",
     "This indicates an outstanding chemical profile: strong alcohol, balanced acidity and well-managed sulphates."),
    (6.0, "Good Quality", "good", "#22d39a",
     "This indicates a balanced chemical composition with favorable characteristics for taste and aroma."),
    (5.0, "Average Quality", "average", "#f5a524",
     "This indicates an acceptable but unremarkable profile. A few properties are holding the score back."),
    (0.0, "Poor Quality", "poor", "#ff5a5f",
     "This chemistry is commonly linked to faults such as excess volatile acidity or low alcohol."),
]


def band_for(score):
    for b in BANDS:
        if score >= b[0]:
            return dict(label=b[1], band=b[2], color=b[3], text=b[4])


def load_data():
    return pd.read_csv(DATA_PATH, sep=";")


def load_metrics():
    return json.loads(METRICS_PATH.read_text())


@lru_cache(maxsize=1)
def load_bundle():
    if not MODEL_PATH.exists():  # first run: train automatically
        from train_model import main
        main()
    return joblib.load(MODEL_PATH)


def predict(bundle, values):
    """Return score, confidence and per-feature contributions for one wine."""
    model = bundle["model"]
    X = pd.DataFrame([values])[FEATURE_KEYS]
    tree_preds = np.array([t.predict(X.values)[0] for t in model.estimators_])
    score = float(np.clip(tree_preds.mean(), 0, 10))
    # confidence = share of trees that agree with the ensemble within +/-0.5
    confidence = float(np.mean(np.abs(tree_preds - score) <= 0.5))
    contribs = {}
    for k in FEATURE_KEYS:  # effect of replacing a feature with its dataset average
        X2 = X.copy()
        X2[k] = bundle["stats"]["mean"][k]
        contribs[k] = float(score - model.predict(X2)[0])
    b = band_for(score)
    return dict(score=score, confidence=confidence, contributions=contribs,
                label=b["label"], version=MODEL_VERSION, type="Red Wine")


def radar_data(bundle, values):
    s = bundle["stats"]
    norm = lambda k, v: float(np.clip((v - s["min"][k]) / (s["max"][k] - s["min"][k]), 0, 1))
    return ([norm(k, values[k]) for k in RADAR_AXES],
            [norm(k, s["ideal"][k]) for k in RADAR_AXES])


def insights(v):
    good, concerns = [], []
    if v["alcohol"] < 12.5:
        good.append("Moderate alcohol content is easier on the body when enjoyed in moderation.")
    if 0.5 <= v["sulphates"] <= 1.0:
        good.append("Sulphates in a typical range act as natural preservatives.")
    good.append("Red wine contains antioxidants (such as polyphenols) that may help reduce inflammation.")
    if v["alcohol"] >= 12.5:
        concerns.append("High alcohol content may affect the liver and brain if consumed excessively.")
    if v["volatile acidity"] > 0.7:
        concerns.append("High volatile acidity gives a vinegar-like taste and can cause stomach irritation.")
    if v["sulphates"] > 1.0 or v["total sulfur dioxide"] > 150:
        concerns.append("Excessive sulfites may trigger reactions in sensitive individuals.")
    if v["chlorides"] > 0.15:
        concerns.append("High chlorides give the wine a salty edge.")
    if not concerns:
        concerns.append("No notable concerns in the entered chemistry.")
    return good, concerns


def recommendations(v):
    out = []
    if v["alcohol"] < 10:
        out.append("Alcohol is low. Wines rated higher usually sit between 10.5% and 13%.")
    if v["volatile acidity"] > 0.6:
        out.append("Volatile acidity is high. Better fermentation hygiene lowers vinegar notes.")
    if v["sulphates"] < 0.6:
        out.append("Sulphates are low. A modest increase improves stability and is linked to higher ratings.")
    if v["citric acid"] < 0.15:
        out.append("Citric acid is low. A small addition can add freshness.")
    if v["total sulfur dioxide"] > 100:
        out.append("Total sulfur dioxide is high. Reduce additions to avoid harsh aromas.")
    return out or ["The profile is well balanced. Keep these levels consistent between batches."]


@lru_cache(maxsize=1)
def top_band():
    """25th percentile, median and 75th percentile of each property among wines rated 7 or more."""
    hi = load_data().query("quality >= 7")
    return {k: (float(hi[k].quantile(.25)), float(hi[k].median()), float(hi[k].quantile(.75))) for k in FEATURE_KEYS}


def explain(values, contribs, n=6):
    """Plain-language reasons behind a score, strongest first."""
    band, items = top_band(), []
    for k, c in sorted(contribs.items(), key=lambda kv: -abs(kv[1]))[:n]:
        lo, med, hi = band[k]
        v = values[k]
        pos = "within" if lo <= v <= hi else ("below" if v < lo else "above")
        if abs(c) < 0.02:
            text = f"{LABEL_OF[k]} ({v:g}) has almost no effect on this score."
        else:
            text = (f"{LABEL_OF[k]} ({v:g}) is {pos} the typical range of top-rated wines "
                    f"({lo:.3g} to {hi:.3g}), which {'raises' if c > 0 else 'lowers'} the predicted score by {abs(c):.2f}.")
        items.append(dict(key=k, label=LABEL_OF[k], effect=c, text=text))
    return items


def what_if(bundle, values, rec, n=3):
    """Single-change scenarios: move one weak property to the typical top-rated value and re-predict."""
    band, out = top_band(), []
    for k, c in sorted(rec["contributions"].items(), key=lambda kv: kv[1])[:5]:
        target = band[k][1]
        if c > -0.02 or abs(target - values[k]) < 1e-9:
            continue
        v2 = {**values, k: target}
        new = float(bundle["model"].predict(pd.DataFrame([v2])[FEATURE_KEYS])[0])
        out.append(dict(key=k, label=LABEL_OF[k], now=values[k], to=target, new_score=new, gain=new - rec["score"]))
    return sorted(out, key=lambda d: -d["gain"])[:n]
