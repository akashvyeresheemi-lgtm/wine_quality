import datetime as dt

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import batch, db, ml, report, standards, style

st.set_page_config(page_title="Alcohol Quality Prediction", page_icon="🍷", layout="wide")
st.markdown(style.CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Training model for first run...")
def bundle():
    return ml.load_bundle()


@st.cache_data
def data():
    return ml.load_data()


@st.cache_data
def metrics():
    return ml.load_metrics()


def fmt_when(iso):
    return dt.datetime.fromisoformat(iso).strftime("%b %d, %Y • %I:%M %p")


def theme(fig, h=300, **kw):
    fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#c3cdf0", size=12), margin=dict(l=10, r=10, t=30, b=10), **kw)
    fig.update_xaxes(gridcolor="#18224a", zeroline=False)
    fig.update_yaxes(gridcolor="#18224a", zeroline=False)
    return fig


def show(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ---------- state ----------
ss = st.session_state
ss.setdefault("page", "Home")
ss.setdefault("vals", dict(ml.DEFAULTS))
ss.setdefault("selected", None)


def make_record(vals, save):
    rec = ml.predict(bundle(), vals)
    rec.update(ts=dt.datetime.now().isoformat(timespec="seconds"), values=dict(vals), id=None)
    if save:
        rec["id"] = db.add(rec)
    return rec


if "current" not in ss:
    ss.current = make_record(ss.vals, save=False)


def goto(page, rec_id=None):
    ss.page, ss.selected = page, rec_id


def load_sample(q):
    row = data()[data().quality == q].iloc[0]
    ss.vals = {k: float(row[k]) for k in ml.FEATURE_KEYS}


# ---------- sidebar ----------
PAGES = [("Home", "home"), ("Predict Quality", "biotech"), ("Batch Prediction", "upload_file"),
         ("Explainability", "psychology"), ("Report", "description"), ("History", "history"),
         ("Analytics", "analytics"), ("About", "info")]
with st.sidebar:
    st.markdown(style.brand(), unsafe_allow_html=True)
    for name, icon in PAGES:
        st.button(name, key=f"nav_{name}", icon=f":material/{icon}:", width="stretch",
                  type="primary" if ss.page == name else "secondary", on_click=goto, args=(name,))
    st.markdown(style.promo(), unsafe_allow_html=True)

st.markdown(style.topbar(), unsafe_allow_html=True)


# ---------- components ----------
def input_panel(key):
    with st.container(key=f"panel_{key}"):
        st.markdown(style.title("⚡", "Quick Prediction", "Enter the wine properties below to predict its quality."),
                    unsafe_allow_html=True)
        with st.form(f"form_{key}", border=False):
            vals = {}
            for i in range(0, len(ml.FEATURES), 3):
                cols = st.columns(3)
                for col, f in zip(cols, ml.FEATURES[i:i + 3]):
                    with col:
                        vals[f["key"]] = st.number_input(f["label"], f["lo"], f["hi"], float(ss.vals[f["key"]]),
                                                         f["step"], format=f["fmt"])
                        st.markdown(f'<div class="rng">({f["lo"]:g} - {f["hi"]:g})</div>', unsafe_allow_html=True)
            go_ = st.form_submit_button("Predict Quality", type="primary", icon=":material/auto_awesome:",
                                        width="stretch")
    if go_:
        ss.vals = vals
        ss.current = make_record(vals, save=True)
        st.rerun()


def result_panel(rec, key):
    b = ml.band_for(rec["score"])
    with st.container(key=f"panel_result_{key}"):
        a, c = st.columns([3, 2])
        a.markdown(style.title("📊", "Prediction Result"), unsafe_allow_html=True)
        c.download_button("Download Report (PDF)", report.build_pdf(rec), "wine_quality_report.pdf",
                          "application/pdf", key=f"dl_top_{key}", icon=":material/description:",
                          width="stretch")
        l, r = st.columns([1, 1.25])
        l.markdown(style.ring(rec["score"], b["color"], b["label"]), unsafe_allow_html=True)
        r.markdown(style.verdict(b["label"], b["band"], b["color"], b["text"], rec["score"], rec["confidence"]),
                   unsafe_allow_html=True)
        st.markdown(style.meta(rec["type"], fmt_when(rec["ts"]), rec["version"]), unsafe_allow_html=True)


def impact_chart(rec, h=330):
    items = sorted(rec["contributions"].items(), key=lambda kv: kv[1])
    fig = go.Figure(go.Bar(
        x=[v for _, v in items], y=[ml.LABEL_OF[k] for k, _ in items], orientation="h",
        marker_color=["#22d39a" if v >= 0 else "#ff6b5e" for _, v in items],
        text=[f"{v:+.2f}" for _, v in items], textposition="outside", cliponaxis=False))
    theme(fig, h)
    fig.update_xaxes(visible=False)
    show(fig)


def radar_chart(rec, h=330):
    mine, ideal = ml.radar_data(bundle(), rec["values"])
    names = [ml.LABEL_OF[k] for k in ml.RADAR_AXES]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=ideal + ideal[:1], theta=names + names[:1], name="Ideal Range",
                                  line=dict(color="#22d39a", dash="dot"), fill="toself",
                                  fillcolor="rgba(34,211,154,.10)"))
    fig.add_trace(go.Scatterpolar(r=mine + mine[:1], theta=names + names[:1], name="Your Sample",
                                  line=dict(color="#4a8cff"), fill="toself", fillcolor="rgba(74,140,255,.25)"))
    theme(fig, h, legend=dict(orientation="h", y=-0.08, x=0.2),
          polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False, range=[0, 1]),
                     angularaxis=dict(gridcolor="#243060")))
    show(fig)


def insights_panel(rec):
    st.markdown(style.insights(*ml.insights(rec["values"])), unsafe_allow_html=True)


def recent_panel(n=4):
    with st.container(key="panel_recent"):
        a, b = st.columns([4, 1])
        a.markdown(style.title("🕒", "Recent Predictions"), unsafe_allow_html=True)
        b.button("View All", key="va", on_click=goto, args=("History",))
        recs = db.all_records(n)
        if not recs:
            st.markdown('<div class="empty">No predictions yet. Enter wine properties and select Predict Quality.</div>',
                        unsafe_allow_html=True)
            return
        h = st.columns([2.2, 1.2, 1.2, 1.4])
        for c, t in zip(h, ["Date & Time", "Quality Score", "Type", "Action"]):
            c.markdown(f'<div class="th">{t}</div>', unsafe_allow_html=True)
        for r in recs:
            c = st.columns([2.2, 1.2, 1.2, 1.4])
            c[0].write(fmt_when(r["ts"])); c[1].write(f"{r['score']:.1f}"); c[2].write(r["type"])
            c[3].button("View Report", key=f"vr_{r['id']}", on_click=goto, args=("Report", r["id"]))


def compliance_panel(rec, key):
    rows = standards.check(rec["values"])
    ver = standards.verdict(rows, rec["score"], rec["values"])
    with st.container(key=f"panel_comp_{key}"):
        st.markdown(style.title("🏛️", "Government Quality Standards Comparison",
                                "Your wine measured against OIV international reference limits. "
                                "† marks advisory guidance or a limit not re-verified. Hover a row for its source."),
                    unsafe_allow_html=True)
        l, r = st.columns([2.4, 1])
        l.markdown(style.compliance_bars(rows), unsafe_allow_html=True)
        r.markdown(style.safety_card(ver), unsafe_allow_html=True)


# ---------- pages ----------
def page_home():
    df = data()
    st.markdown(style.html("""<div class="welcome"><span class="glass">🍷</span><div><h1>Welcome to Alcohol Quality Prediction</h1>
    <p>Analyze the chemical properties of wine and predict its quality using machine learning.</p></div></div>"""),
                unsafe_allow_html=True)
    cards = [("s-blue", "🧪", "Total Samples", f"{len(df):,}", "Wine samples in dataset"),
             ("s-green", "⭐", "Average Quality", f"{df.quality.mean():.2f}", "(out of 10)"),
             ("s-purple", "🎯", "Best Quality", f"{df.quality.max()}", "(observed in dataset)"),
             ("s-red", "⚠️", "Lowest Quality", f"{df.quality.min()}", "(observed in dataset)")]
    for col, c in zip(st.columns(4), cards):
        col.markdown(style.stat(*c), unsafe_allow_html=True)
    st.write("")
    l, r = st.columns([1.1, 1])
    with l:
        input_panel("home")
    with r:
        result_panel(ss.current, "home")
    st.write("")
    a, b, c = st.columns([1.15, 1.15, 1])
    with a, st.container(key="panel_impact"):
        st.markdown(style.title("📈", "Feature Impact on Prediction", "How each property influenced the quality score."),
                    unsafe_allow_html=True)
        impact_chart(ss.current)
    with b, st.container(key="panel_radar"):
        st.markdown(style.title("🕸️", "Feature Analysis", "Your wine properties compared to the profile of top-rated wines."),
                    unsafe_allow_html=True)
        radar_chart(ss.current)
    with c, st.container(key="panel_health"):
        st.markdown(style.title("💚", "Health & Safety Insights"), unsafe_allow_html=True)
        insights_panel(ss.current)
    st.write("")
    compliance_panel(ss.current, "home")
    st.write("")
    a, b = st.columns([1, 2.3])
    with a, st.container(key="panel_dl"):
        st.markdown(style.title("📄", "Download Your Report",
                                "Get a detailed PDF report with prediction results, feature analysis, health insights and recommendations."),
                    unsafe_allow_html=True)
        st.download_button("Download PDF Report", report.build_pdf(ss.current), "wine_quality_report.pdf",
                           "application/pdf", key="dl_bottom", type="primary", icon=":material/download:",
                           width="stretch")
    with b:
        recent_panel()


def page_predict():
    st.markdown("### Predict Quality")
    st.caption("Type your own values or start from a real sample in the dataset.")
    c = st.columns(4)
    c[0].button("Load lowest-rated sample", on_click=load_sample, args=(int(data().quality.min()),), width="stretch")
    c[1].button("Load average sample", on_click=load_sample, args=(5,), width="stretch")
    c[2].button("Load good sample", on_click=load_sample, args=(6,), width="stretch")
    c[3].button("Load top-rated sample", on_click=load_sample, args=(int(data().quality.max()),), width="stretch")
    l, r = st.columns([1.1, 1])
    with l:
        input_panel("predict")
    with r:
        result_panel(ss.current, "predict")
    a, b, c3 = st.columns([1.15, 1.15, 1])
    with a, st.container(key="panel_impact2"):
        st.markdown(style.title("📈", "Feature Impact on Prediction"), unsafe_allow_html=True); impact_chart(ss.current)
    with b, st.container(key="panel_radar2"):
        st.markdown(style.title("🕸️", "Feature Analysis"), unsafe_allow_html=True); radar_chart(ss.current)
    with c3, st.container(key="panel_health2"):
        st.markdown(style.title("💚", "Health & Safety Insights"), unsafe_allow_html=True); insights_panel(ss.current)


def page_report():
    recs = db.all_records()
    rec = db.get(ss.selected) if ss.selected else None
    if rec is None and recs:
        rec = recs[0]
    if rec is None:
        rec = ss.current
        st.info("No saved predictions yet, so this report shows the default sample.")
    st.markdown("### Prediction Report")
    if recs:
        opts = {f"#{r['id']} • {fmt_when(r['ts'])} • {r['score']:.1f}": r["id"] for r in recs}
        pick = st.selectbox("Choose a prediction", list(opts), index=list(opts.values()).index(rec["id"]) if rec["id"] in opts.values() else 0)
        rec = db.get(opts[pick])
    result_panel(rec, "report")
    l, r = st.columns(2)
    with l, st.container(key="panel_rimp"):
        st.markdown(style.title("📈", "Feature Impact"), unsafe_allow_html=True); impact_chart(rec)
    with r, st.container(key="panel_rrec"):
        st.markdown(style.title("✅", "Recommendations"), unsafe_allow_html=True)
        for t in ml.recommendations(rec["values"]):
            st.markdown(f"- {t}")
        insights_panel(rec)
    with st.expander("Input properties"):
        st.dataframe(pd.DataFrame({"Property": [ml.LABEL_OF[k] for k in ml.FEATURE_KEYS],
                                   "Value": [rec["values"][k] for k in ml.FEATURE_KEYS]}), hide_index=True)


def page_history():
    st.markdown("### Prediction History")
    recs = db.all_records()
    if not recs:
        st.info("No predictions yet. Run one from Home or Predict Quality.")
        return
    df = pd.DataFrame([{"ID": r["id"], "Date & Time": fmt_when(r["ts"]), "Score": round(r["score"], 2),
                        "Rating": r["label"], "Confidence": f"{r['confidence'] * 100:.0f}%", "Type": r["type"],
                        **{ml.LABEL_OF[k]: r["values"][k] for k in ml.FEATURE_KEYS}} for r in recs])
    flt = st.multiselect("Filter by rating", sorted(df["Rating"].unique()), default=sorted(df["Rating"].unique()))
    view = df[df["Rating"].isin(flt)]
    st.dataframe(view, hide_index=True, width="stretch")
    a, b, _ = st.columns([1, 1, 3])
    a.download_button("Export CSV", view.to_csv(index=False), "prediction_history.csv", "text/csv", width="stretch")
    if b.button("Clear history", width="stretch"):
        db.clear(); st.rerun()
    fig = px.line(df.iloc[::-1], x="Date & Time", y="Score", markers=True, title="Score over time")
    fig.update_traces(line_color="#6a55f2"); show(theme(fig, 280))


def page_analytics():
    df, m = data(), metrics()
    st.markdown("### Analytics")
    t1, t2, t3, t4 = st.tabs(["Dataset", "Feature explorer", "Model performance", "Feature importance"])
    with t1:
        a, b = st.columns(2)
        counts = df.quality.value_counts().sort_index()
        fig = px.bar(x=counts.index.astype(str), y=counts.values, labels=dict(x="Quality", y="Samples"),
                     title="Quality distribution", color_discrete_sequence=["#6a55f2"])
        a.plotly_chart(theme(fig, 340), width="stretch", config={"displayModeBar": False})
        fig = px.imshow(df.corr(), text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                        title="Correlation matrix")
        b.plotly_chart(theme(fig, 340), width="stretch", config={"displayModeBar": False})
        st.dataframe(df.describe().T.round(3), width="stretch")
    with t2:
        feat = st.selectbox("Property", ml.FEATURE_KEYS, format_func=ml.LABEL_OF.get, index=10)
        a, b = st.columns(2)
        fig = px.box(df, x="quality", y=feat, color_discrete_sequence=["#4a8cff"], title=f"{ml.LABEL_OF[feat]} by quality")
        a.plotly_chart(theme(fig, 380), width="stretch", config={"displayModeBar": False})
        fig = px.histogram(df, x=feat, nbins=40, color_discrete_sequence=["#22d39a"], title="Distribution")
        b.plotly_chart(theme(fig, 380), width="stretch", config={"displayModeBar": False})
    with t3:
        f = m["final"]
        k = st.columns(4)
        k[0].metric("R²", f"{f['r2']:.3f}"); k[1].metric("RMSE", f"{f['rmse']:.3f}")
        k[2].metric("MAE", f"{f['mae']:.3f}"); k[3].metric("Within ±0.5", f"{f['within_half'] * 100:.0f}%")
        comp = pd.DataFrame(m["comparison"]).rename(columns=dict(model="Model", cv_rmse="CV RMSE", rmse="Test RMSE",
                                                                  mae="Test MAE", r2="Test R²", within_half="Within ±0.5"))
        st.dataframe(comp.round(3), hide_index=True, width="stretch")
        fig = px.scatter(x=m["test_actual"], y=m["test_pred"], opacity=.5, labels=dict(x="Actual", y="Predicted"),
                         title="Predicted vs actual (held-out test set)", color_discrete_sequence=["#6a55f2"])
        fig.add_shape(type="line", x0=3, y0=3, x1=8, y1=8, line=dict(color="#22d39a", dash="dot"))
        show(theme(fig, 380))
        st.caption(f"Deployed model: tuned Random Forest {m['best_params']}. Trained on {m['n_train']} samples, "
                   f"tested on {m['n_test']}.")
    with t4:
        imp = pd.Series(m["importances"]).rename(index=ml.LABEL_OF).sort_values()
        fig = px.bar(x=imp.values, y=imp.index, orientation="h", title="Global feature importance",
                     color_discrete_sequence=["#6a55f2"], labels=dict(x="Importance", y=""))
        show(theme(fig, 420))


def page_about():
    st.markdown("### About")
    st.markdown("""
**Alcohol Quality Prediction** estimates the sensory quality score (0–10) of red wine from 11 physicochemical measurements.

- **Data:** UCI Wine Quality (red), 1,599 samples.
- **Model:** tuned Random Forest regressor, benchmarked against Ridge, Gradient Boosting and Extra Trees.
- **Confidence:** the share of trees whose prediction is within ±0.5 of the ensemble score.
- **Safety and standards:** each property is compared with OIV reference limits (dagger marks advisory or unverified ones). The verdict is a screening, not a lab test.
- **Batch prediction:** upload a CSV and every row is scored, rated and safety-checked.
- **Feature impact:** how much the score changes when one property is replaced by the dataset average.
- **Stack:** Python, scikit-learn, Streamlit, Plotly, SQLite, ReportLab.

**Limits.** The data contains red wine only, scores are subjective expert ratings, and very low or very high
scores are rare, so predictions regress toward 5–7. Health notes are general information, not medical advice.
""")


def page_explain():
    rec = ss.current
    b = ml.band_for(rec["score"])
    st.markdown("### Explainability")
    c = st.columns([4, 1])
    c[0].caption(f"Explaining the wine from Predict Quality: predicted {rec['score']:.1f} / 10, {b['label']}.")
    c[1].button("Change wine", on_click=goto, args=("Predict Quality",), width="stretch")
    compliance_panel(rec, "explain")
    st.write("")
    l, r = st.columns([1.1, 1])
    with l, st.container(key="panel_why"):
        st.markdown(style.title("🔍", "What is affecting the quality score",
                                "Each property compared with the typical range of wines rated 7 or more."),
                    unsafe_allow_html=True)
        items = ml.explain(rec["values"], rec["contributions"])
        st.markdown(style.explain_list(items), unsafe_allow_html=True)
        up = max(rec["contributions"].items(), key=lambda kv: kv[1])
        dn = min(rec["contributions"].items(), key=lambda kv: kv[1])
        st.markdown(f"**Biggest boost:** {ml.LABEL_OF[up[0]]} ({up[1]:+.2f}). **Biggest drag:** {ml.LABEL_OF[dn[0]]} ({dn[1]:+.2f}).")
    with r, st.container(key="panel_whyimp"):
        st.markdown(style.title("📈", "Impact of each property", "Green raises the score, red lowers it."),
                    unsafe_allow_html=True)
        impact_chart(rec, 380)
    st.write("")
    with st.container(key="panel_whatif"):
        st.markdown(style.title("🧪", "What would improve it",
                                "Change one property to the typical top-rated value and the model re-predicts. "
                                "This is a model estimate, not winemaking advice."), unsafe_allow_html=True)
        wi = ml.what_if(bundle(), rec["values"], rec)
        if wi:
            st.dataframe(pd.DataFrame([{"Property": w["label"], "Now": round(w["now"], 3), "Try": round(w["to"], 3),
                                        "New score": round(w["new_score"], 2), "Gain": f"{w['gain']:+.2f}"} for w in wi]),
                         hide_index=True, width="stretch")
        else:
            st.markdown('<div class="empty">No single property change would raise this score noticeably.</div>',
                        unsafe_allow_html=True)
    st.caption(standards.DISCLAIMER)


RATING_COLORS = {"Excellent Quality": "#22d39a", "Good Quality": "#6df0c2", "Average Quality": "#f5a524", "Poor Quality": "#ff5a5f"}
SAFETY_COLORS = {"Safe": "#22d39a", "Caution": "#f5a524", "Not recommended": "#ff5a5f"}


def page_batch():
    st.markdown("### Batch Prediction")
    st.caption("Upload a CSV with the 11 physicochemical properties. Every wine gets a predicted quality, rating, "
               "confidence and safety check.")
    with st.container(key="panel_batch_up"):
        a, b = st.columns([3, 1])
        up = a.file_uploader("CSV file", type=["csv", "txt"], label_visibility="collapsed")
        b.download_button("Download template", batch.template_csv(), "wine_template.csv", "text/csv", width="stretch")
        if b.button("Use sample data", width="stretch"):
            ss.batch_sample = True
        st.caption("Required columns: " + ", ".join(ml.FEATURE_KEYS) + ". Comma or semicolon separated. "
                   "Column names are matched ignoring case, spaces and underscores. "
                   "An optional quality column adds an accuracy check.")
    if up is not None:
        ss.batch_sample = False
        try:
            raw = pd.read_csv(up, sep=None, engine="python")
        except Exception as e:
            st.error(f"Could not read this file as CSV ({e}). Check that it is a text CSV with a header row.")
            return
    elif ss.get("batch_sample"):
        raw = data().sample(200, random_state=1).reset_index(drop=True)
        st.info("Showing 200 random rows from the training dataset. Accuracy looks better here than on new wines.")
    else:
        st.info("Upload a CSV or choose Use sample data to see results.")
        return
    df, missing = batch.prepare(raw)
    if missing:
        st.error("Missing columns: " + ", ".join(missing))
        st.write("Columns found in your file:", ", ".join(map(str, raw.columns)))
        return
    res, skipped = batch.run(bundle(), df)
    if res.empty:
        st.error("No valid rows. Every row had a missing or non-numeric value in the 11 property columns.")
        return
    if skipped:
        st.warning(f"{skipped} row(s) were skipped because of missing or non-numeric values.")
    if len(df) > batch.MAX_ROWS:
        st.warning(f"Only the first {batch.MAX_ROWS:,} rows were processed.")
    k = st.columns(4)
    k[0].metric("Wines predicted", f"{len(res):,}")
    k[1].metric("Average quality", f"{res.predicted_quality.mean():.2f}")
    k[2].metric("Good or better", f"{(res.predicted_quality >= 6).mean() * 100:.0f}%")
    k[3].metric("Flagged (caution or not recommended)", f"{(res.safety != 'Safe').sum():,}")
    l, r = st.columns(2)
    order = [x for x in RATING_COLORS if x in set(res.rating)]
    cnt = res.rating.value_counts().reindex(order)
    fig = go.Figure(go.Bar(x=cnt.index, y=cnt.values, marker_color=[RATING_COLORS[x] for x in cnt.index]))
    with l, st.container(key="panel_b1"):
        st.markdown(style.title("📊", "Quality ratings"), unsafe_allow_html=True); show(theme(fig, 300))
    sc = res.safety.value_counts()
    fig = go.Figure(go.Pie(labels=sc.index, values=sc.values, hole=.6, marker_colors=[SAFETY_COLORS[x] for x in sc.index]))
    with r, st.container(key="panel_b2"):
        st.markdown(style.title("🛡️", "Safety screening"), unsafe_allow_html=True); show(theme(fig, 300))
    if "actual_quality" in res and res.actual_quality.notna().any():
        t = res.dropna(subset=["actual_quality"])
        err = t.predicted_quality - t.actual_quality
        ss_res, ss_tot = (err ** 2).sum(), ((t.actual_quality - t.actual_quality.mean()) ** 2).sum()
        with st.container(key="panel_b3"):
            st.markdown(style.title("🎯", "Accuracy against your quality column"), unsafe_allow_html=True)
            m = st.columns(3)
            m[0].metric("MAE", f"{err.abs().mean():.3f}")
            m[1].metric("Within ±0.5", f"{(err.abs() <= 0.5).mean() * 100:.0f}%")
            m[2].metric("R²", f"{1 - ss_res / ss_tot:.3f}" if ss_tot else "n/a")
            fig = px.scatter(t, x="actual_quality", y="predicted_quality", opacity=.5, color_discrete_sequence=["#6a55f2"])
            fig.add_shape(type="line", x0=3, y0=3, x1=8, y1=8, line=dict(color="#22d39a", dash="dot"))
            show(theme(fig, 300))
    st.markdown("#### Results")
    show_cols = ["row", "predicted_quality", "rating", "confidence_pct", "safety", "safety_note"] + \
                (["actual_quality"] if "actual_quality" in res else []) + ml.FEATURE_KEYS
    st.dataframe(res[show_cols], hide_index=True, width="stretch", column_config={
        "predicted_quality": st.column_config.ProgressColumn("Predicted", min_value=0, max_value=10, format="%.2f"),
        "confidence_pct": st.column_config.NumberColumn("Confidence %", format="%d")})
    st.download_button("Download results (CSV)", res.to_csv(index=False), "wine_predictions.csv", "text/csv",
                       type="primary", icon=":material/download:")
    st.markdown("#### Inspect one wine")
    row = st.selectbox("Row number", res["row"].tolist())
    vals = {k: float(res.loc[res["row"] == row, k].iloc[0]) for k in ml.FEATURE_KEYS}
    rec = ml.predict(bundle(), vals)
    rec.update(ts=dt.datetime.now().isoformat(timespec="seconds"), values=vals, id=None)
    compliance_panel(rec, "batch")
    for e in ml.explain(vals, rec["contributions"], 4):
        st.markdown(f"- {e['text']}")


{"Home": page_home, "Predict Quality": page_predict, "Batch Prediction": page_batch, "Explainability": page_explain, "Report": page_report,
 "History": page_history, "Analytics": page_analytics, "About": page_about}[ss.page]()
