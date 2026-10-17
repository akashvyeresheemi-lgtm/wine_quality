"""Dark dashboard theme and small HTML components."""

def html(s):
    return " ".join(line.strip() for line in s.splitlines())


CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(1200px 600px at 70% -10%, #121a3d 0%, #080d1f 55%); }
header[data-testid="stHeader"], #MainMenu, footer { display: none; }
.block-container { padding: 0 1.6rem 2rem 1.6rem; max-width: 100%; }
section[data-testid="stSidebar"] { background: #0a1128; border-right: 1px solid #1a2447; width: 250px !important; }
section[data-testid="stSidebar"] > div { padding-top: 0.6rem; }
section[data-testid="stSidebar"] .stButton > button {
  justify-content: flex-start; background: transparent; border: 0; color: #c3cdf0; font-weight: 500;
  padding: .7rem .9rem; border-radius: 10px; }
section[data-testid="stSidebar"] .stButton > button:hover { background: #131c3e; color: #fff; }
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(90deg,#3f3bd6,#4a4ff0); color: #fff; box-shadow: 0 6px 18px #2a2fb855; }
.brand { display:flex; gap:12px; align-items:center; padding: 14px 6px 18px 6px; border-bottom:1px solid #1a2447; margin-bottom:14px; }
.brand .logo { font-size: 34px; } .brand b { font-size: 17px; display:block; line-height:1.15; } .brand span { font-size:17px; color:#c3cdf0; }
.topbar { display:flex; justify-content:space-between; align-items:center; padding: 14px 4px; border-bottom:1px solid #1a2447; margin: 0 -1.6rem 18px; padding-left:1.6rem; padding-right:1.6rem; }
.topbar b { font-size:15px; } .topbar small { color:#8b97c2; display:block; font-size:12px; }
.user { display:flex; gap:10px; align-items:center; font-size:13px; }
.avatar { width:30px; height:30px; border-radius:50%; background:linear-gradient(135deg,#4a8cff,#7a5cff); display:inline-block; }
.welcome { display:flex; gap:16px; align-items:center; margin-bottom:16px; }
.welcome h1 { font-size: 26px; margin:0; font-weight:700; } .welcome p { margin:2px 0 0; color:#9aa6d1; font-size:14px; }
.welcome .glass { font-size:42px; }
[class*="st-key-panel"] { background: linear-gradient(180deg,#0f1733,#0c1330); border:1px solid #1d2a54; border-radius:14px; padding: 18px 20px; }
.ptitle { font-weight:600; font-size:16px; margin:0; display:flex; gap:10px; align-items:center; }
.psub { color:#8b97c2; font-size:12.5px; margin: 2px 0 12px; }
.stat { display:flex; gap:14px; align-items:center; border:1px solid #1d2a54; border-radius:14px; padding:18px; height:100%; }
.stat .ic { width:50px; height:50px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:22px; flex:none; }
.stat small { color:#aab4dc; font-size:12.5px; } .stat b { display:block; font-size:24px; line-height:1.25; } .stat em { font-style:normal; color:#8b97c2; font-size:11.5px; }
.s-blue { background: linear-gradient(135deg,#101a45,#0d1331);} .s-blue .ic{background:#2f55d4;}
.s-green { background: linear-gradient(135deg,#0c2a2d,#0c1630);} .s-green .ic{background:#17b583;}
.s-purple { background: linear-gradient(135deg,#1a1648,#0e1233);} .s-purple .ic{background:#6c4fe0;}
.s-red { background: linear-gradient(135deg,#251428,#0e1233);} .s-red .ic{background:#e2434f;}
.stNumberInput label p, .stSelectbox label p { font-size:12.5px !important; color:#c3cdf0; }
.stNumberInput input { background:#0a1028 !important; border-radius:8px; }
.stNumberInput div[data-baseweb="input"] { background:#0a1028; border:1px solid #243060; border-radius:8px; }
.rng { color:#6f7ba6; font-size:11px; margin:-10px 0 6px; }
.stForm { border:0 !important; padding:0 !important; }
.stButton > button[kind="primary"], .stFormSubmitButton > button, .stDownloadButton > button[kind="primary"] {
  background: linear-gradient(90deg,#5446e8,#6a55f2); color:#fff; border:0; border-radius:10px; font-weight:600; padding:.65rem 1rem; }
.stDownloadButton > button { border:1px solid #2b3868; background:#0d1430; border-radius:8px; color:#e6ebff; }
.ring { position:relative; width:210px; height:210px; margin:auto; }
.ring svg { width:100%; height:100%; filter: drop-shadow(0 0 10px var(--c)); }
.ring .t { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }
.ring .t small { color:#c3cdf0; font-size:13px; } .ring .t b { font-size:38px; line-height:1.2; } .ring .t b span { font-size:18px; color:#c3cdf0; font-weight:500; }
.verdict { border:1px solid var(--c); background:color-mix(in srgb, var(--c) 9%, #0c1330); border-radius:12px; padding:14px 16px; }
.verdict small { color:#c3cdf0; } .verdict h3 { margin:0 0 8px; font-size:20px; color:var(--c); } .verdict p { font-size:13px; color:#d4dbf5; margin:0; line-height:1.55; }
.conf { border:1px solid #1d2a54; border-radius:12px; padding:12px 16px; margin-top:12px; font-size:13px; }
.conf .row { display:flex; justify-content:space-between; margin-bottom:8px; }
.bar { height:9px; border-radius:6px; background:#18224a; } .bar i { display:block; height:100%; border-radius:6px; background:linear-gradient(90deg,#22d39a,#6df0c2); }
.meta { display:flex; border:1px solid #1d2a54; border-radius:12px; margin-top:14px; }
.meta div { flex:1; padding:12px 16px; font-size:12.5px; border-right:1px solid #1d2a54; } .meta div:last-child { border:0; }
.meta small { color:#8b97c2; display:block; }
.good { border:1px solid #1f7a5c; background:#0b2a2e; border-radius:10px; padding:12px 14px; font-size:12.5px; margin-bottom:10px; }
.warn { border:1px solid #8a6210; background:#2a2310; border-radius:10px; padding:12px 14px; font-size:12.5px; margin-bottom:10px; }
.note { border:1px solid #1f4c8a; background:#0c1f3d; border-radius:10px; padding:10px 14px; font-size:11.5px; color:#7fb2ff; }
.good b { color:#22d39a; } .warn b { color:#f5a524; }
.good li, .warn li { margin:5px 0; color:#d4dbf5; } .good ul, .warn ul { margin:6px 0 0; padding-left:18px; }
.promo { border:1px solid #1d2a54; border-radius:12px; padding:16px; margin-top:60px; background:linear-gradient(180deg,#0e1633,#2a0f22); }
.promo b { display:block; font-size:15px; margin:8px 0 6px; } .promo small { color:#aab4dc; font-size:12px; }
.empty { color:#8b97c2; font-size:13px; padding:14px 0; }
.th { color:#8b97c2; font-size:12px; border-bottom:1px solid #1d2a54; padding-bottom:6px; margin-bottom:4px; }
[class*="st-key-panel"] .stButton > button { padding:.15rem .6rem; font-size:12px; border:1px solid #2b3868; background:#0d1430; color:#9fb4ff; border-radius:6px; }

.cr{display:grid;grid-template-columns:165px 1fr 70px;gap:4px 12px;align-items:center;margin-bottom:10px}
.cr .cl b{font-size:13px;display:block}.cr .cl span{font-size:11.5px;color:#8b97c2}
.ct{position:relative;height:12px;background:#18224a;border-radius:7px}
.ct .zone{position:absolute;top:0;height:100%;background:rgba(34,211,154,.2);border-radius:7px}
.ct .fill{position:absolute;left:0;top:0;height:100%;width:var(--w);border-radius:7px;animation:grow 1.2s cubic-bezier(.2,.8,.2,1) var(--d) both}
.ct .lim{position:absolute;top:-4px;width:2px;height:20px;background:#fff;opacity:.85;border-radius:1px}
.fill.ok{background:linear-gradient(90deg,#17b583,#6df0c2)}
.fill.near{background:linear-gradient(90deg,#d98a0b,#ffcf66)}
.fill.fail{background:linear-gradient(90deg,#d6334a,#ff7a85);animation:grow 1.2s cubic-bezier(.2,.8,.2,1) var(--d) both,pulse 1.8s ease-in-out calc(var(--d) + 1.3s) infinite}
@keyframes grow{from{width:0}to{width:var(--w)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(255,90,95,0)}50%{box-shadow:0 0 12px 2px rgba(255,90,95,.6)}}
.chip{font-size:11.5px;font-weight:600;text-align:center;padding:3px 8px;border-radius:20px}
.chip.ok{background:#0e3a30;color:#22d39a}.chip.near{background:#3a2c0b;color:#f5a524}.chip.fail{background:#3d1520;color:#ff6b6b}
.lt{grid-column:2;font-size:11px;color:#6f7ba6;margin-top:-2px}
.legend{display:flex;gap:16px;font-size:11.5px;color:#8b97c2;margin-bottom:12px}.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.sc{border-radius:14px;padding:18px;border:1px solid var(--c);background:color-mix(in srgb,var(--c) 10%,#0c1330)}
.sc .ic{font-size:32px}.sc h3{margin:6px 0 8px;color:var(--c);font-size:19px}
.sc ul{margin:0;padding-left:18px;font-size:12.5px;color:#d4dbf5}.sc li{margin:5px 0}
.sc .pc{margin-top:12px;font-size:12px;color:#c3cdf0}.sc .bar{margin-top:6px}.sc small{display:block;color:#8b97c2;font-size:11px;margin-top:10px;line-height:1.5}
.xl .item{display:flex;gap:10px;margin:0 0 12px;font-size:13px;line-height:1.55;color:#d4dbf5}
.xl .up{color:#22d39a;font-weight:700}.xl .dn{color:#ff6b5e;font-weight:700}
@media (prefers-reduced-motion:reduce){.ct .fill{animation:none!important}}
</style>"""


def brand():
    return html('<div class="brand"><span class="logo">🍷</span><div><b>Alcohol Quality</b><span>Prediction</span></div></div>')


def topbar():
    return html("""<div class="topbar"><div><b>Alcohol Quality Prediction</b><small>AI Powered Wine Quality Analysis</small></div>
    <div class="user"><span class="avatar"></span>Guest User</div></div>""")


def promo():
    return html("""<div class="promo">🍃<b>Better Choices<br>Healthier Tomorrow</b>
    <small>Know what you drink.<br>Make informed decisions.</small><div style="font-size:54px;margin-top:10px">🍇🍷</div></div>""")


def title(icon, text, sub=""):
    return html(f'<p class="ptitle">{icon} {text}</p><p class="psub">{sub}</p>')


def stat(cls, icon, label, value, note):
    return html(f'<div class="stat {cls}"><div class="ic">{icon}</div><div><small>{label}</small><b>{value}</b><em>{note}</em></div></div>')


def ring(score, color, label):
    c = 502.65
    return html(f"""<div class="ring" style="--c:{color}"><svg viewBox="0 0 200 200">
    <circle cx="100" cy="100" r="80" fill="none" stroke="#18224a" stroke-width="10"/>
    <circle cx="100" cy="100" r="80" fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round"
    stroke-dasharray="{c * score / 10:.1f} {c}" transform="rotate(-90 100 100)"/></svg>
    <div class="t"><small>Predicted Quality</small><b>{score:.1f} <span>/ 10</span></b><small style="color:{color};font-weight:600">{label}</small></div></div>""")


def verdict(label, band, color, text, score, conf):
    return html(f"""<div class="verdict" style="--c:{color}"><small>This wine is likely to be of</small><h3>✔ {label}</h3>
    <p>The predicted quality score is <b>{score:.1f}</b> out of 10, which falls in the <b style="color:{color}">{band}</b> range. {text}</p></div>
    <div class="conf"><div class="row"><span>Confidence</span><b>{conf * 100:.0f}%</b></div><div class="bar"><i style="width:{conf * 100:.0f}%"></i></div></div>""")


def meta(rtype, when, version):
    return html(f"""<div class="meta"><div><small>Type</small>🍷 {rtype}</div><div><small>Prediction Date</small>{when}</div>
    <div><small>Model Version</small>{version}</div></div>""")


def insights(good, concerns):
    g = "".join(f"<li>{t}</li>" for t in good)
    w = "".join(f"<li>{t}</li>" for t in concerns)
    return html(f"""<div class="good"><b>✔ Good for Health</b> (in moderate amounts)<ul>{g}</ul></div>
    <div class="warn"><b>⚠ Potential Concerns</b><ul>{w}</ul></div>
    <div class="note">Note: Health effects depend on consumption amount, individual tolerance, and overall lifestyle.</div>""")


def compliance_bars(rows):
    out = ['<div class="legend"><span><i style="background:rgba(34,211,154,.35)"></i>Allowed zone</span>'
           '<span><i style="background:#fff;width:3px"></i>Limit</span>'
           '<span><i style="background:#17b583"></i>Pass</span><span><i style="background:#d98a0b"></i>Watch</span>'
           '<span><i style="background:#d6334a"></i>Fail</span></div>']
    for i, r in enumerate(rows):
        v, lo, hi = r["value"], r["lo"], r["hi"]
        top = max((hi * 1.5) if r["kind"] == "max" else (lo * 2) if r["kind"] == "min" else hi * 1.4, v * 1.1)
        pct = lambda x: min(100, 100 * x / top)
        if r["kind"] == "max":
            zl, zw, lim = 0, pct(hi), pct(hi)
        elif r["kind"] == "min":
            zl, zw, lim = pct(lo), 100 - pct(lo), pct(lo)
        else:
            zl, zw, lim = pct(lo), pct(hi) - pct(lo), pct(hi)
        unit = f" {r['unit']}" if r["unit"] else ""
        out.append(
            f'<div class="cr" style="--d:{i * 0.09:.2f}s" title="{r["source"]}">'
            f'<div class="cl"><b>{r["label"]}</b><span>{v:g}{unit}</span></div>'
            f'<div class="ct"><i class="zone" style="left:{zl:.1f}%;width:{zw:.1f}%"></i>'
            f'<i class="fill {r["status"]}" style="--w:{pct(v):.1f}%"></i><i class="lim" style="left:{lim:.1f}%"></i></div>'
            f'<div class="chip {r["status"]}">{r["status_text"]}</div><div class="lt">{r["limit_text"]} &middot; {r["source"]}</div></div>')
    return html("".join(out))


def safety_card(v):
    li = "".join(f"<li>{t}</li>" for t in v["reasons"])
    return html(f"""<div class="sc" style="--c:{v['color']}"><div class="ic">{v['icon']}</div><h3>{v['title']}</h3><ul>{li}</ul>
    <div class="pc">{v['ok_pct']}% of checks passed</div><div class="bar"><i style="width:{v['ok_pct']}%;background:{v['color']}"></i></div>
    <small>Screening against OIV reference limits, not a lab test or safety certificate. Alcohol is harmful in excess.</small></div>""")


def explain_list(items):
    rows = "".join(
        f'<div class="item"><span class="{"up" if e["effect"] >= 0 else "dn"}">{"&#9650;" if e["effect"] >= 0 else "&#9660;"}</span>'
        f'<span>{e["text"]}</span></div>' for e in items)
    return html(f'<div class="xl">{rows}</div>')
