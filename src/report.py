"""PDF report generation."""
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import ml, standards

INDIGO = colors.HexColor("#4338ca")


def build_pdf(rec):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm, title="Wine Quality Report")
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=INDIGO, alignment=0, fontSize=22)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=INDIGO, spaceBefore=14)
    body = ss["BodyText"]
    band = ml.band_for(rec["score"])
    when = datetime.fromisoformat(rec["ts"]).strftime("%b %d, %Y %I:%M %p")

    def table(rows, widths, header=True):
        t = Table(rows, colWidths=widths)
        style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                 ("FONTSIZE", (0, 0), (-1, -1), 9), ("PADDING", (0, 0), (-1, -1), 5),
                 ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")])]
        if header:
            style += [("BACKGROUND", (0, 0), (-1, 0), INDIGO), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
        t.setStyle(TableStyle(style))
        return t

    good, concerns = ml.insights(rec["values"])
    s = [Paragraph("Alcohol Quality Prediction Report", h1),
         Paragraph(f"Generated {when} &bull; Model {rec['version']} &bull; {rec['type']}", body),
         Paragraph("Prediction result", h2),
         table([["Predicted quality", "Rating", "Confidence"],
                [f"{rec['score']:.1f} / 10", band["label"], f"{rec['confidence'] * 100:.0f}%"]],
               [60 * mm, 60 * mm, 50 * mm]),
         Spacer(1, 6), Paragraph(f"The predicted score falls in the <b>{band['band']}</b> range. {band['text']}", body),
         Paragraph("Input properties", h2),
         table([["Property", "Value"]] + [[ml.LABEL_OF[k], f"{rec['values'][k]:g}"] for k in ml.FEATURE_KEYS],
               [85 * mm, 85 * mm]),
         Paragraph("Feature impact on prediction", h2)]
    ranked = sorted(rec["contributions"].items(), key=lambda kv: -kv[1])
    s.append(table([["Property", "Impact on score"]] + [[ml.LABEL_OF[k], f"{v:+.2f}"] for k, v in ranked],
                   [85 * mm, 85 * mm]))
    rows = standards.check(rec["values"])
    ver = standards.verdict(rows, rec["score"], rec["values"])
    s += [Paragraph("Safety &amp; regulatory check", h2), Paragraph(f"<b>{ver['title']}</b>", body)]
    s += [Paragraph(f"&bull; {t}", body) for t in ver["reasons"]]
    s += [Spacer(1, 6), table([["Parameter", "Value", "Reference limit", "Status"]] +
          [[r["label"], f"{r['value']:g} {r['unit']}".strip(), r["limit_text"], r["status_text"]] for r in rows],
          [48 * mm, 38 * mm, 48 * mm, 36 * mm]),
          Paragraph("<i>Reference limits: OIV International Code of Oenological Practices. A dagger marks advisory "
                    "guidance or a limit not re-verified. " + standards.DISCLAIMER + "</i>", body)]
    s += [Paragraph("What is driving this score", h2)]
    s += [Paragraph(f"&bull; {e['text']}", body) for e in ml.explain(rec["values"], rec["contributions"])]
    s += [Paragraph("Health &amp; safety insights", h2)]
    s += [Paragraph(f"&#10003; {t}", body) for t in good]
    s += [Paragraph(f"&#9888; {t}", body) for t in concerns]
    s += [Paragraph("Recommendations", h2)]
    s += [Paragraph(f"&bull; {t}", body) for t in ml.recommendations(rec["values"])]
    s += [Spacer(1, 12), Paragraph(
        "<i>Disclaimer: predictions come from a machine-learning model trained on the UCI Red Wine Quality "
        "dataset. They are an estimate, not a laboratory or medical assessment.</i>", body)]
    doc.build(s)
    return buf.getvalue()
