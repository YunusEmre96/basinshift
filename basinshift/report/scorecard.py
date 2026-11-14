"""Risk ve Su Karnesi: seçilen planın tek sayfalık PDF özeti.

Banka, sigorta (ör. TARSİM) veya kooperatif için: kural uyumu, kötü dönem
geliri, tahmini su kullanımı, destek ve toprak sağlığı. Karbon iddiası İÇERMEZ.
Türkçe karakterler için matplotlib ile gelen DejaVu Sans fontu kullanılır.
"""
from __future__ import annotations

import io
import os
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from fpdf import FPDF  # noqa: E402

from ..explain.why import ds_name
from ..explain.fmt import area_factor, merged_year, money, num, water  # noqa: E402

INK = (31, 42, 36)
MUTED = (107, 122, 112)
WATER = (28, 93, 122)
STATUS_RGB = {"green": (46, 125, 79), "yellow": (227, 181, 5), "red": (179, 57, 47)}
TXT = {
    "tr": {
        "title": "Risk ve Su Karnesi", "farm": "İşletme", "site": "Konum", "basin": "Havza", "date": "Tarih",
        "area": "Alan", "plan": "Plan", "status": "Kural durumu", "metric": "Gösterge", "this": "Bu plan",
        "current": "Mevcut plan", "mean": "Ortalama brüt kâr / yıl", "bad": "Kötü dönem geliri / yıl (CVaR %5)",
        "water": "Sulama suyu / yıl", "water4": "4 yıllık sulama suyu (tarla)", "support": "Tahmini destek / yıl",
        "loss": "Zarar eden yıl olasılığı", "soil": "Toprak sağlığı", "why": "Neden bu plan", "gaps": "Bilgi boşlukları",
        "dist": "4 yıllık toplam brüt kâr: geçmiş dönemler", "synthetic": "UYARI: Bu karne SENTETİK demo verisiyle üretildi; gerçek karar için kullanılmamalıdır.",
        "disclaimer": "BasinShift seçenekleri ve gerekçelerini gösterir; kararın sahibi çiftçi ve yerel ziraat mühendisidir. Tahminler model çıktısıdır; fiyatlar 2026 varsayımıdır. Karbon iddiası içermez.",
        "status_green": "Kurallara uygun", "status_yellow": "Sarı kart riski", "status_red": "Kırmızı kart riski",
        "nitrogen": "Azot", "organic_matter": "Organik madde", "erosion": "Erozyon/çıplak toprak", "pest_cycle": "Zararlı döngüsü",
        "data": "Veri", "years": "hasat yılı",
        "defaults": "Şu değerler ölçülmedi, elle girilmiş varsayımdır: {}.",
        "placeholders": "Not: Şu veri setleri sentetik yer tutucudur (iklim ve yağış gerçek NASA verisidir): {}.",
    },
    "en": {
        "title": "Risk and Water Scorecard", "farm": "Farm", "site": "Location", "basin": "Basin", "date": "Date",
        "area": "Area", "plan": "Plan", "status": "Rule status", "metric": "Indicator", "this": "This plan",
        "current": "Current plan", "mean": "Average gross margin / yr", "bad": "Bad-period income / yr (CVaR 5%)",
        "water": "Irrigation water / yr", "water4": "4-year irrigation water (field)", "support": "Estimated support / yr",
        "loss": "Chance of a loss year", "soil": "Soil health", "why": "Why this plan", "gaps": "Information gaps",
        "dist": "4-year total gross margin across historical periods", "synthetic": "WARNING: This scorecard uses SYNTHETIC demo data; do not use for real decisions.",
        "disclaimer": "BasinShift shows options and reasons; the decision belongs to the farmer and local agronomist. Estimates are model outputs; prices are 2026 assumptions. No carbon claims.",
        "status_green": "Compliant", "status_yellow": "Yellow card risk", "status_red": "Red card risk",
        "nitrogen": "Nitrogen", "organic_matter": "Organic matter", "erosion": "Erosion/bare soil", "pest_cycle": "Pest cycle",
        "data": "Data", "years": "harvest years",
        "defaults": "These values are not measured but hand-entered assumptions: {}.",
        "placeholders": "Note: these datasets are synthetic placeholders (climate and rainfall are real NASA data): {}.",
    },
}


def _font_path() -> str:
    return os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans.ttf")


def _font_bold_path() -> str:
    return os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans-Bold.ttf")


def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _dist_png(option, current, f: float, sym: str, unit: str, labels: tuple[str, str]) -> bytes:
    fig, ax = plt.subplots(figsize=(7.4, 1.95), dpi=150)
    data, names, colors = [], [], []
    if current is not None:
        data.append(current.detail["sim"]["margin"].sum(axis=1) * f)
        names.append(labels[1])
        colors.append("#8A97B4")
    data.append(option.detail["sim"]["margin"].sum(axis=1) * f)
    names.append(labels[0])
    colors.append("#0960E1")
    try:
        bp = ax.boxplot(data, orientation="horizontal", patch_artist=True, widths=0.55, medianprops=dict(color="#E43700", linewidth=1.6))
    except TypeError:  # matplotlib < 3.10
        bp = ax.boxplot(data, vert=False, patch_artist=True, widths=0.55, medianprops=dict(color="#E43700", linewidth=1.6))
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c + "33")
        patch.set_edgecolor(c)
    ax.set_yticks(range(1, len(names) + 1), names, fontsize=8)
    ax.tick_params(axis="x", labelsize=7)
    ax.set_xlabel(f"{sym}/{unit}", fontsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return buf.getvalue()


def build_scorecard_pdf(option, current, ctx, expl: dict, provenance: dict, lang: str = "tr", unit: str = "da",
                        farmer: str = "", field_area: float = 100.0, title: str = "") -> bytes:
    L = TXT[lang]
    sym = ctx.basin.currency_symbol
    f = area_factor(unit)
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(True, margin=12)
    pdf.add_font("DejaVu", "", _font_path())
    pdf.add_font("DejaVu", "B", _font_bold_path())
    pdf.add_page()
    pdf.set_margins(14, 12, 14)

    # Başlık bandı (Space Apps marka renkleri: Deep Blue zemin, Neon Yellow vurgu)
    pdf.set_fill_color(7, 23, 63)
    pdf.rect(0, 0, 210, 27, "F")
    pdf.set_fill_color(0, 66, 166)
    pdf.rect(0, 27, 210, 1.6, "F")
    pdf.set_fill_color(234, 254, 7)
    pdf.rect(14, 27, 34, 1.6, "F")
    pdf.set_xy(14, 6)
    pdf.set_font("DejaVu", "B", 7.5)
    pdf.set_text_color(234, 254, 7)
    pdf.cell(0, 4, "NASA SPACE APPS CHALLENGE 2026 · FIELD SHIFT · KONYA", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, f"BasinShift · {L['title']}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(31)
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(*MUTED)
    meta = [f"{L['date']}: {date.today().isoformat()}", f"{L['site']}: {ctx.site.name} ({ctx.site.lat:.3f}, {ctx.site.lon:.3f})",
            f"{L['basin']}: {ctx.basin.name(lang)}", f"{L['area']}: {num(field_area, lang)} {unit}"]
    if farmer:
        meta.insert(0, f"{L['farm']}: {farmer}")
    pdf.multi_cell(0, 4.6, "   |   ".join(meta), new_x="LMARGIN", new_y="NEXT")

    warn = []
    clim = provenance.get("climate_daily")
    if clim is not None and clim.is_synthetic:
        warn.append(L["synthetic"])
    else:
        ph = [ds_name(ds, lang) for ds, p in provenance.items() if p.is_synthetic]
        if ph:
            warn.append(L["placeholders"].format(", ".join(ph)))
    defaults = [ds_name(ds, lang) for ds, p in provenance.items() if p.is_default]
    if defaults:
        warn.append(L["defaults"].format(", ".join(defaults)))
    if warn:
        pdf.ln(1)
        pdf.set_fill_color(251, 246, 223)
        pdf.set_text_color(90, 70, 0)
        pdf.set_font("DejaVu", "B", 9)
        pdf.multi_cell(0, 5, "  ".join(warn), fill=True, new_x="LMARGIN", new_y="NEXT")

    # Plan şeridi
    pdf.ln(2)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 7, f"{L['plan']}: {title}", new_x="LMARGIN", new_y="NEXT")
    years = ctx.settings.plan_years
    w = (pdf.w - pdf.l_margin - pdf.r_margin) / len(years)
    y0 = pdf.get_y()
    for i, yr in enumerate(years):
        if len(option.parts) == 1:
            c = ctx.crops[option.parts[0][0][i]]
            label = c.name(lang)
        else:
            m = merged_year(option.parts, i)
            c = ctx.crops[m[0][0]]
            label = c.name(lang) if len(m) == 1 else " + ".join(f"{s * 100:.0f}% {ctx.crops[cid].name(lang)}" for cid, s in m)
        rgb = _hex(c.color)
        lum = (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255
        pdf.set_fill_color(*rgb)
        pdf.set_text_color(*(INK if lum > 0.55 else (255, 255, 255)))
        pdf.set_xy(pdf.l_margin + i * w, y0)
        pdf.set_font("DejaVu", "", 7)
        pdf.cell(w - 1, 4, str(yr), fill=True, new_x="LEFT", new_y="NEXT")
        pdf.set_x(pdf.l_margin + i * w)
        pdf.set_font("DejaVu", "B", 8)
        pdf.multi_cell(w - 1, 4.2, label, fill=True, new_x="LEFT", new_y="NEXT")
    pdf.set_y(y0 + 15)
    st_rgb = STATUS_RGB[option.detail["status"]]
    pdf.set_fill_color(*st_rgb)
    pdf.rect(pdf.l_margin, pdf.get_y() + 0.8, 3, 4.2, style="F")
    pdf.set_x(pdf.l_margin + 5)
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 6, f"{L['status']}: {L['status_' + option.detail['status']]}", new_x="LMARGIN", new_y="NEXT")

    # Gösterge tablosu
    pdf.ln(2)
    m = option.metrics
    c = current.metrics if current is not None and option.key != "current" else None
    rows = [
        (L["mean"], money(m["mean_margin"], sym, unit, lang), money(c["mean_margin"], sym, unit, lang) if c else "—"),
        (L["bad"], money(m["cvar5"], sym, unit, lang), money(c["cvar5"], sym, unit, lang) if c else "—"),
    ]
    if ctx.settings.irrigated:
        rows.append((L["water"], water(m["water_mean"], unit, lang), water(c["water_mean"], unit, lang) if c else "—"))
        fa = field_area / f
        rows.append((L["water4"], f"{num(m['water_total'] * fa, lang)} m³", f"{num(c['water_total'] * fa, lang)} m³" if c else "—"))
    rows += [
        (L["support"], money(m["support_mean"], sym, unit, lang), money(c["support_mean"], sym, unit, lang) if c else "—"),
        (L["loss"], f"{m['loss_prob'] * 100:.0f}%", f"{c['loss_prob'] * 100:.0f}%" if c else "—"),
        (L["soil"], f"{option.detail['soil']['soil']:.0f}/100", f"{current.detail['soil']['soil']:.0f}/100" if c else "—"),
    ]
    widths = (86, 48, 48)
    pdf.set_font("DejaVu", "B", 9)
    pdf.set_fill_color(226, 237, 252)
    for txt, wd in zip((L["metric"], L["this"], L["current"]), widths):
        pdf.cell(wd, 6, txt, border=0, fill=True)
    pdf.ln()
    pdf.set_font("DejaVu", "", 9)
    for r in rows:
        for txt, wd in zip(r, widths):
            pdf.cell(wd, 5.6, txt, border="B")
        pdf.ln()

    # Toprak alt skorları
    pdf.ln(2)
    soil = option.detail["soil"]
    pdf.set_font("DejaVu", "", 8)
    bar_w = 40
    x = pdf.l_margin
    for k in ("nitrogen", "organic_matter", "erosion", "pest_cycle"):
        pdf.set_xy(x, pdf.get_y())
        pdf.set_text_color(*MUTED)
        pdf.cell(bar_w, 4, f"{L[k]}  {soil[k]:.0f}")
        yb = pdf.get_y() + 4.4
        pdf.set_fill_color(214, 222, 236)
        pdf.rect(x, yb, bar_w - 4, 1.8, style="F")
        pdf.set_fill_color(0, 66, 166)
        pdf.rect(x, yb, (bar_w - 4) * max(0, min(100, soil[k])) / 100, 1.8, style="F")
        x += bar_w + 4
    pdf.ln(9)

    # Dağılım grafiği
    pdf.set_text_color(*INK)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 6, L["dist"], new_x="LMARGIN", new_y="NEXT")
    png = _dist_png(option, current if option.key != "current" else None, f, sym, unit, (L["this"], L["current"]))
    pdf.image(io.BytesIO(png), w=pdf.w - pdf.l_margin - pdf.r_margin)

    # Neden / bilgi boşlukları
    def bullets(head: str, lines: list[str], limit: int):
        pdf.set_font("DejaVu", "B", 10)
        pdf.set_text_color(*INK)
        pdf.cell(0, 6, head, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "", 8.5)
        for ln in lines[:limit]:
            pdf.multi_cell(0, 4.3, f"• {ln}", new_x="LMARGIN", new_y="NEXT")

    bullets(L["why"], expl.get("why", []) + expl.get("benefits", [])[:2], 6)
    bullets(L["gaps"], expl.get("gaps", []), 4)

    cp = provenance.get("climate_daily")
    pdf.ln(1)
    pdf.set_font("DejaVu", "", 7.5)
    pdf.set_text_color(*MUTED)
    yrs = ctx.table.years
    pdf.multi_cell(0, 3.8, f"{L['data']}: {cp.product_text(lang) if cp else ''} ({cp.label(lang) if cp else ''}), "
                           f"{yrs[0]}–{yrs[-1]} {L['years']}; FAO-56 / FAO-33. " + L["disclaimer"],
                   new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
