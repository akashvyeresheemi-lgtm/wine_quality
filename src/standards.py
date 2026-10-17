"""Reference limits (OIV) and the safety verdict.

legal=True   -> limit comes from the OIV Code / Compendium (pass or fail)
legal=False  -> advisory winemaking guidance only (never a hard fail)
hazard=True  -> exceeding it makes the wine "not recommended"
confirmed    -> False for limits not re-checked against the OIV text (shown with a dagger)
Edit LIMITS to apply a different national standard (for example FSSAI, EU or TTB).
"""
from .ml import LABEL_OF


def _l(key, kind, unit, source, lo=None, hi=None, legal=True, hazard=False, confirmed=True):
    return dict(key=key, kind=kind, unit=unit, source=source, lo=lo, hi=hi,
                legal=legal, hazard=hazard, confirmed=confirmed)


LIMITS = [
    _l("volatile acidity", "max", "g/L", "OIV: 20 meq/L, about 1.2 g/L as acetic acid", hi=1.2, hazard=True),
    _l("total sulfur dioxide", "max", "mg/L", "OIV: 150 mg/L for red wine (up to 4 g/L sugar)", hi=150, hazard=True),
    _l("citric acid", "max", "g/L", "OIV: 1 g/L", hi=1.0, hazard=True),
    _l("sulphates", "max", "g/L", "OIV: 1 g/L as potassium sulphate", hi=1.0, hazard=True, confirmed=False),
    _l("chlorides", "max", "g/L", "OIV: 1 g/L as sodium chloride", hi=1.0, hazard=True, confirmed=False),
    _l("alcohol", "min", "% vol", "OIV wine definition: at least 8.5% vol", lo=8.5),
    _l("fixed acidity", "min", "g/L", "OIV: total acidity at least 3.5 g/L tartaric", lo=3.5, legal=False, confirmed=False),
    _l("residual sugar", "max", "g/L", "Dry wine: up to 4 g/L (OIV/EU class)", hi=4.0, legal=False),
    _l("pH", "range", "", "Typical stable red wine range", lo=2.9, hi=3.9, legal=False),
    _l("free sulfur dioxide", "range", "mg/L", "Typical red wine range", lo=10, hi=50, legal=False),
]

DISCLAIMER = ("This is a screening against international reference limits, not a laboratory test or a "
              "safety certificate. National rules differ, so check the authority that applies to you. "
              "Alcohol is harmful in excess, and some people should avoid it entirely.")


def check(values):
    rows = []
    for L in LIMITS:
        v, lo, hi = float(values[L["key"]]), L["lo"], L["hi"]
        if L["kind"] == "max":
            bad, near, limit = v > hi, v >= 0.85 * hi, f"max {hi:g} {L['unit']}"
        elif L["kind"] == "min":
            bad, near, limit = v < lo, v <= 1.1 * lo, f"min {lo:g} {L['unit']}"
        else:
            bad, near, limit = not (lo <= v <= hi), False, f"{lo:g} to {hi:g} {L['unit']}".strip()
        near = near and L["legal"]  # advisory items only turn amber when outside their typical range
        status = "fail" if bad and L["legal"] else "near" if (bad or near) else "ok"
        rows.append(dict(L, label=LABEL_OF[L["key"]] + ("" if L["confirmed"] and L["legal"] else " \u2020"),
                         value=v, limit_text=limit, status=status,
                         status_text={"ok": "Pass", "near": "Watch", "fail": "Fail"}[status]))
    return rows


def verdict(rows, score, values):
    fails = [r for r in rows if r["status"] == "fail" and r["hazard"]]
    watch = [r for r in rows if r["legal"] and r["status"] != "ok" and r not in fails]
    reasons = []
    for r in fails:
        reasons.append(f"{r['label'].replace(' \u2020', '')} is {r['value']:g} {r['unit']}, above the {r['hi']:g} {r['unit']} limit.")
    for r in watch:
        name = r["label"].replace(" \u2020", "")
        if r["status"] == "fail":
            reasons.append(f"{name} is {r['value']:g} {r['unit']}, below the {r['lo']:g} {r['unit']} minimum for wine.")
        else:
            reasons.append(f"{name} is close to its limit ({r['limit_text']}).")
    if values["alcohol"] >= 14:
        reasons.append("Alcohol is high. Limit how much you drink.")
    if score < 5 and not fails:
        reasons.append("The predicted quality is low, so taste faults are likely.")
    ok_pct = round(100 * sum(r["status"] == "ok" for r in rows) / len(rows))
    if fails:
        return dict(level="unsafe", title="Not recommended to drink", color="#ff5a5f", icon="\u26d4",
                    reasons=reasons, ok_pct=ok_pct, short="Not recommended")
    if reasons:
        return dict(level="caution", title="Drink with caution", color="#f5a524", icon="\u26a0\ufe0f",
                    reasons=reasons, ok_pct=ok_pct, short="Caution")
    return dict(level="safe", title="Within safe reference limits", color="#22d39a", icon="\u2705",
                reasons=["Every checked property is inside its reference limit or typical range."],
                ok_pct=ok_pct, short="Safe")
