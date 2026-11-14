"""BasinShift Kılavuzu (Sürüm 3.1) — HTML + Chrome ile PDF üretimi.

Kullanım:  python build.py <ekran_görüntüsü_klasörü> <çıktı.pdf>
Adımlar: ekran görüntülerinden kırpmalar → SVG şekiller → kapak + gövde PDF (Chrome/playwright)
→ içindekiler sayfa numaraları (pdftotext ile) → ikinci geçiş → birleştirme (pypdf).
"""
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
SHOTS = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/shots/final")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else HERE / "BasinShift_Kilavuz.pdf")
IMG = HERE / "img"
IMG.mkdir(exist_ok=True)

# ---------------------------------------------------------------- kırpmalar
X0, X1 = 360, 1540
CROPS = {
    "sidebar": ("01_field.png", (0, 0, 300, 1265)),
    "field_hero": ("00_field_top.png", (0, 0, 1600, 1000)),
    "field_form": ("01_field.png", (X0, 495, X1, 1565)),
    "status_top": ("05_status.png", (X0, 300, X1, 850)),
    "status_mid": ("05_status.png", (X0, 880, X1, 1690)),
    "status_precip": ("05_status.png", (X0, 1710, X1, 2290)),
    "plans_top": ("03_plans.png", (X0, 140, X1, 795)),
    "plans_cards": ("03_plans.png", (X0, 820, X1, 1690)),
    "plans_violin": ("03_plans.png", (X0, 1715, X1, 2200)),
    "plans_pareto": ("10_pareto.png", (X0, 690, X1, 1200)),
    "futures": ("06_futures.png", (X0, 140, X1, 1640)),
    "basin_top": ("07_basin.png", (X0, 320, X1, 860)),
    "basin_bars": ("07_basin.png", (X0, 860, X1, 1520)),
    "basin_cobweb": ("07_basin.png", (X0, 1530, X1, 2390)),
    "basin_coop": ("07_basin.png", (X0, 2400, X1, 3270)),
    "basin_trade": ("07_basin.png", (X0, 3290, X1, 4450)),
    "crops": ("05b_crops.png", (X0, 140, X1, 1530)),
    "crops_chart": ("05b_crops.png", (X0, 1505, X1, 2090)),
    "plans_price": ("03_plans.png", (X0, 2160, X1, 2850)),
    "report": ("08_report.png", (X0, 460, X1, 1990)),
    "method": ("09_method.png", (X0, 180, X1, 1440)),
}


def _open(fn: str) -> Image.Image:
    p = SHOTS / fn
    if not p.exists():
        p = p.with_suffix(".jpg")
    return Image.open(p).convert("RGB")


def make_crops(overrides: dict | None = None) -> None:
    crops = dict(CROPS, **(overrides or {}))
    for name, (fn, box) in crops.items():
        im = _open(fn)
        x0, y0, x1, y1 = box
        im.crop((x0, y0, min(x1, im.width), min(y1, im.height))).save(IMG / f"{name}.jpg", quality=88, optimize=True)
    # Denge kartının "Neden bu plan?" sütunu → yan yana üç şerit
    why = _open("04_plans_why.png")
    col = why.crop(WHY_BOX)
    n = 3
    h = (col.height + n - 1) // n
    sheet = Image.new("RGB", (col.width * n + 24 * (n - 1), h), (5, 13, 38))
    for i in range(n):
        part = col.crop((0, i * h, col.width, min(col.height, (i + 1) * h)))
        sheet.paste(part, (i * (col.width + 24), 0))
    sheet.save(IMG / "plans_why.jpg", quality=88, optimize=True)


WHY_BOX = (1238, 1545, 1532, 5285)

# ---------------------------------------------------------------- SVG şekiller
FONT = 'font-family="Inter"'


def status_svg() -> str:
    items = [("Gerçek NASA", 4, "#1E9E5A", "POWER · IMERG · GRACE · CMIP6"),
             ("Sentetik yer tutucu", 2, "#D9A400", "SMAP · HLS/MODIS NDVI"),
             ("Varsayım", 2, "#8794AE", "SRTM eğimi · Çumra toprağı")]
    x, parts, legend = 0, [], []
    W = 640
    for i, (lab, n, col, sub) in enumerate(items):
        w = W * n / 8
        parts.append(f'<rect x="{x + 20}" y="18" width="{w - 4}" height="30" rx="6" fill="{col}"/>'
                     f'<text x="{x + 20 + (w - 4) / 2}" y="38" text-anchor="middle" font-size="13" font-weight="800" fill="#fff">{n}</text>')
        legend.append(f'<circle cx="{30 + i * 215}" cy="72" r="5" fill="{col}"/><text x="{40 + i * 215}" y="76" font-size="11" font-weight="700" fill="#0B1633">{lab}</text>'
                      f'<text x="{40 + i * 215}" y="91" font-size="9.5" fill="#4B5A78">{sub}</text>')
        x += w
    return f'<svg viewBox="0 0 680 100" xmlns="http://www.w3.org/2000/svg" {FONT}>{"".join(parts)}{"".join(legend)}</svg>'


def ratio_svg() -> str:
    ratios = [0.30, 0.32, 0.60, 0.93, 1.02, 1.50, 1.22, 1.38, 0.90, 0.75, 0.55, 0.51]
    months = "Oca Şub Mar Nis May Haz Tem Ağu Eyl Eki Kas Ara".split()
    W, H, L, B = 680, 210, 50, 175
    sy = lambda v: B - v / 1.6 * 150
    out = [f'<line x1="{L}" y1="{sy(1)}" x2="{W - 10}" y2="{sy(1)}" stroke="#0B1633" stroke-dasharray="4 3"/>'
           f'<text x="{W - 12}" y="{sy(1) - 5}" text-anchor="end" font-size="9.5" fill="#0B1633">oran = 1 (düzeltme yok)</text>']
    for v in (0, 0.5, 1.0, 1.5):
        out.append(f'<text x="{L - 8}" y="{sy(v) + 3}" text-anchor="end" font-size="9" fill="#4B5A78">{str(v).replace(".", ",")}</text>'
                   f'<line x1="{L}" y1="{sy(v)}" x2="{W - 10}" y2="{sy(v)}" stroke="#D5DEEE" stroke-width="0.6"/>')
    bw = (W - L - 20) / 12
    for i, (m, v) in enumerate(zip(months, ratios)):
        x = L + 6 + i * bw
        col = "#E43700" if v in (0.30, 1.50) else ("#0960E1" if v < 1 else "#2E96F5")
        out.append(f'<rect x="{x}" y="{sy(v)}" width="{bw - 12}" height="{B - sy(v)}" rx="3" fill="{col}"/>'
                   f'<text x="{x + (bw - 12) / 2}" y="{sy(v) - 4}" text-anchor="middle" font-size="9" font-weight="700" fill="#0B1633">{str(v).replace(".", ",")}</text>'
                   f'<text x="{x + (bw - 12) / 2}" y="{B + 14}" text-anchor="middle" font-size="9.5" fill="#4B5A78">{m}</text>')
    out.append(f'<text x="12" y="{sy(0.8)}" font-size="9.5" fill="#4B5A78" transform="rotate(-90 12 {sy(0.8)})" text-anchor="middle">IMERG / POWER</text>')
    out.append(f'<text x="{L}" y="12" font-size="11" font-weight="800" fill="#07173F">Çumra · aylık düzeltme oranları (kırmızı: kırpma sınırı)</text>')
    return f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" {FONT}>{"".join(out)}</svg>'


def box(x, y, w, h, title, sub="", fill="#07173F", tc="#fff", sc="#AFC3EE", stroke="none", r=10, fs=11.5):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
    if sub:
        s += (f'<text x="{x + w / 2}" y="{y + h / 2 - 3}" text-anchor="middle" font-size="{fs}" font-weight="800" fill="{tc}">{title}</text>'
              f'<text x="{x + w / 2}" y="{y + h / 2 + 12}" text-anchor="middle" font-size="9" fill="{sc}">{sub}</text>')
    else:
        s += f'<text x="{x + w / 2}" y="{y + h / 2 + 4}" text-anchor="middle" font-size="{fs}" font-weight="800" fill="{tc}">{title}</text>'
    return s


ARROW = ('<defs><marker id="m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
         '<path d="M0,0 L10,5 L0,10 z" fill="#0042A6"/></marker></defs>')


def arr(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#0042A6" stroke-width="1.6" marker-end="url(#m)"/>'


def pipeline_svg() -> str:
    B, Y, D = "#0960E1", "#EAFE07", "#07173F"
    s = [ARROW]
    s.append(box(10, 10, 150, 46, "NASA POWER", "günlük iklim 1981–", B))
    s.append(box(10, 66, 150, 46, "GPM IMERG", "uydu yağışı 2000–", B))
    s.append(box(10, 122, 150, 46, "NEX-GDDP-CMIP6", "2040'lar katsayıları", B))
    s.append(box(10, 178, 150, 46, "SoilGrids / SMAP", "toprak, başlangıç nemi", "#2E96F5"))
    s.append(box(10, 250, 150, 46, "tables/", "crops · ekonomi · kurallar", Y, "#07173F", "#4B5A78"))
    s.append(box(200, 38, 150, 50, "İklim + düzeltme", "IMERG oranı, senaryo", D))
    s.append(box(200, 108, 150, 50, "ET₀ (FAO-56)", "Penman-Monteith", D))
    s.append(box(200, 178, 150, 50, "Su dengesi", "ürün × yıl (12 × 44)", D))
    s.append(box(390, 108, 150, 50, "Verim · gelir", "FAO-33, stres, destek", D))
    s.append(box(390, 178, 150, 50, "20.736 plan", "41 dönem × 4 yıl", D))
    s.append(box(390, 250, 150, 46, "Kurallar + koşullar", "sarı / kırmızı kart", D))
    s.append(box(580, 108, 100, 50, "Pareto", "5.324 → 125", "#0042A6"))
    s.append(box(580, 178, 100, 50, "Kartlar", "Kâr·Akifer·Denge", Y, "#07173F", "#4B5A78"))
    s.append(box(580, 250, 100, 46, "Açıklama", "+ PDF karne", "#0042A6"))
    s += [arr(160, 33, 198, 55), arr(160, 89, 198, 66), arr(160, 145, 198, 76), arr(275, 88, 275, 106),
          arr(275, 158, 275, 176), arr(160, 201, 198, 203), arr(160, 268, 388, 270), arr(160, 262, 198, 222),
          arr(350, 203, 388, 136), arr(465, 158, 465, 176), arr(540, 203, 578, 140), arr(465, 228, 465, 248),
          arr(540, 268, 578, 214), arr(630, 228, 630, 248)]
    return f'<svg viewBox="0 0 690 305" xmlns="http://www.w3.org/2000/svg" {FONT}>{"".join(s)}</svg>'


def cards_svg() -> str:
    s = [ARROW]
    rows = [("Bütün dizilimler", "12 ürün⁴", "20.736", 640), ("Kurala ve koşullara uyan", "yeşil + yem + ara verme", "5.324", 470),
            ("Pareto cephesi", "kâr↑ CVaR↑ su↓ toprak↑", "125", 300)]
    for i, (a, b, n, w) in enumerate(rows):
        x = (680 - w) / 2
        y = 8 + i * 50
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="42" rx="8" fill="{["#E6EEFB", "#C9DCFA", "#0960E1"][i]}"/>')
        tc = "#fff" if i == 2 else "#07173F"
        s.append(f'<text x="{x + 14}" y="{y + 18}" font-size="11.5" font-weight="800" fill="{tc}">{a}</text>'
                 f'<text x="{x + 14}" y="{y + 33}" font-size="9" fill="{"#DCE7FF" if i == 2 else "#4B5A78"}">{b}</text>'
                 f'<text x="{x + w - 14}" y="{y + 28}" text-anchor="end" font-size="17" font-weight="900" fill="{tc}">{n}</text>')
    cy = 182
    cards = [("▲ Kâr", "en yüksek ortalama kâr", "#EAFE07", "#07173F"),
             ("◆ Akifer", "kâr ≥ %50 · CVaR ≥ 0 · zarar ≤ %30 → en az su", "#2E96F5", "#fff"),
             ("⬢ Denge", "ağırlıklı skor en yüksek (+ tarla bölme)", "#1E9E5A", "#fff")]
    for i, (t, sub, col, tc) in enumerate(cards):
        x = 20 + i * 220
        s.append(f'<rect x="{x}" y="{cy}" width="200" height="56" rx="10" fill="{col}"/>'
                 f'<text x="{x + 100}" y="{cy + 23}" text-anchor="middle" font-size="13" font-weight="900" fill="{tc}">{t}</text>'
                 f'<text x="{x + 100}" y="{cy + 41}" text-anchor="middle" font-size="8.6" fill="{tc}">{sub}</text>')
        s.append(arr(340, 150, x + 100, cy - 2))
    s.append('<text x="340" y="262" text-anchor="middle" font-size="9.5" fill="#4B5A78">Kartlar birbirinden farklı plan olmak zorunda; mevcut plan ayrıca aynı ölçüyle hesaplanır.</text>')
    return f'<svg viewBox="0 0 680 270" xmlns="http://www.w3.org/2000/svg" {FONT}>{"".join(s)}</svg>'


def basin_svg() -> str:
    data = [("Bugünkü desen", 3241, 428, "#8A97B4"), ("Herkes kendi başına", 2307, 410, "#E43700"),
            ("Koordineli plan", 2623, 278, "#1E9E5A")]
    s = ['<text x="20" y="16" font-size="11" font-weight="800" fill="#07173F">Ortalama brüt kâr (₺/da/yıl)</text>',
         '<text x="370" y="16" font-size="11" font-weight="800" fill="#07173F">Sulama suyu (m³/da/yıl)</text>']
    for i, (lab, k, w, col) in enumerate(data):
        y = 30 + i * 40
        kw = k / 3400 * 230
        ww = w / 450 * 230
        s.append(f'<text x="20" y="{y + 17}" font-size="9.5" fill="#0B1633">{lab}</text>'
                 f'<rect x="120" y="{y + 4}" width="{kw}" height="20" rx="4" fill="{col}"/>'
                 f'<text x="{124 + kw}" y="{y + 19}" font-size="10" font-weight="800" fill="#07173F">{k:,}</text>'.replace(",", "."))
        s.append(f'<rect x="370" y="{y + 4}" width="{ww}" height="20" rx="4" fill="{col}"/>'
                 f'<text x="{374 + ww}" y="{y + 19}" font-size="10" font-weight="800" fill="#07173F">{w}</text>')
    bx = 370 + 278 / 450 * 230
    s.append(f'<line x1="{bx}" y1="26" x2="{bx}" y2="152" stroke="#0042A6" stroke-dasharray="4 3"/>'
             f'<text x="{bx + 4}" y="164" font-size="9" fill="#0042A6">sürdürülebilir bütçe 278</text>')
    return f'<svg viewBox="0 0 680 172" xmlns="http://www.w3.org/2000/svg" {FONT}>{"".join(s)}</svg>'


def arch_svg() -> str:
    s = [ARROW]
    s.append(box(240, 8, 200, 40, "ui/  ·  app.py", "Streamlit sayfaları, tema, i18n", "#0042A6"))
    s.append(box(20, 78, 150, 44, "report/", "PDF karne", "#07173F"))
    s.append(box(190, 78, 150, 44, "explain/", "Neden bu plan?", "#07173F"))
    s.append(box(360, 78, 150, 44, "optimizer/", "Pareto, kartlar", "#07173F"))
    s.append(box(530, 78, 130, 44, "basin/", "LP, cobweb", "#07173F"))
    s.append(box(190, 150, 320, 44, "engine/", "ET₀, su dengesi, verim, risk, toprak, senaryo, pipeline", "#07173F"))
    s.append(box(20, 222, 300, 44, "data/ (DataHub + Provenance)", "nasa · files (KAYNAK.yaml) · synthetic", "#2E96F5"))
    s.append(box(340, 222, 320, 44, "knowledge/ + tables/", "ürün, ekonomi, kural paketleri (YAML)", "#EAFE07", "#07173F", "#4B5A78"))
    s += [arr(300, 48, 95, 76), arr(320, 48, 265, 76), arr(360, 48, 435, 76), arr(400, 48, 595, 76),
          arr(435, 122, 400, 148), arr(265, 122, 300, 148), arr(595, 122, 490, 148), arr(95, 122, 150, 220),
          arr(300, 194, 200, 220), arr(400, 194, 480, 220)]
    return f'<svg viewBox="0 0 680 272" xmlns="http://www.w3.org/2000/svg" {FONT}>{"".join(s)}</svg>'


# ---------------------------------------------------------------- birleştirme
def assemble(toc_pages: dict[str, int] | None = None) -> str:
    body = "".join((HERE / f"part{i}.html").read_text(encoding="utf-8") for i in (1, 2, 3))
    body = (body.replace("{{STATUS_SVG}}", status_svg()).replace("{{RATIO_SVG}}", ratio_svg())
            .replace("{{PIPELINE_SVG}}", pipeline_svg()).replace("{{CARDS_SVG}}", cards_svg())
            .replace("{{BASIN_SVG}}", basin_svg()).replace("{{ARCH_SVG}}", arch_svg()))
    rows = []
    for m in re.finditer(r'data-toc="([^|]+)\|([^|]+)\|([^"]+)"', body):
        num, title, sub = m.groups()
        pg = (toc_pages or {}).get(num, "")
        cls = "row ap" if num.startswith("Ek") else "row"
        rows.append(f'<div class="{cls}"><div class="n">{num}</div><div class="h">{title}<span>{sub}</span></div>'
                    f'<div class="p">{pg}</div></div>')
    body = body.replace("{{TOC}}", "".join(rows))
    css = (HERE / "style.css").read_text(encoding="utf-8")
    return f'<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


HEADER = ('<div style="width:100%;font-family:Inter;font-size:7px;color:#8794AE;padding:0 17mm;display:flex;'
          'justify-content:space-between;-webkit-print-color-adjust:exact"><span><b style="color:#0042A6">BasinShift</b> · Kullanım ve Teknik Kılavuz</span>'
          '<span>NASA Space Apps Challenge 2026 · Field Shift · Konya</span></div>')
FOOTER = ('<div style="width:100%;font-family:Inter;font-size:7px;color:#8794AE;padding:0 17mm;display:flex;'
          'justify-content:space-between;align-items:center"><span>Sürüm 3.1 · 14 Kasım 2026</span>'
          '<span style="color:#07173F;font-weight:800;font-size:8px"><span class="pageNumber"></span> <span style="color:#8794AE;font-weight:400">/ <span class="totalPages"></span></span></span></div>')


def render(html_path: Path, pdf_path: Path, header: bool) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = b.new_page()
        pg.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        pg.wait_for_timeout(600)
        kw = dict(path=str(pdf_path), format="A4", print_background=True, prefer_css_page_size=True)
        if header:
            kw.update(display_header_footer=True, header_template=HEADER, footer_template=FOOTER)
        pg.pdf(**kw)
        b.close()


def find_pages(pdf: Path, html: str, offset: int) -> dict[str, int]:
    """Her bölüm başlığının (h1) gövde PDF'indeki sayfası; kapak sayfası kadar kaydırılır."""
    heads = re.findall(r'data-toc="([^|]+)\|[^"]*">\s*<div class="chap-head"><div class="num">[^<]*</div><div class="kicker">[^<]*</div>\s*<h1>([^<]+)</h1>', html)
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    texts = [subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
             for i in range(1, n + 1)]
    found, start = {}, 2
    for num, title in heads:
        t = re.sub(r"\s+", " ", title.replace("&amp;", "&")).strip()
        key = t[:22]
        for i in range(start, n + 1):
            if key in re.sub(r"\s+", " ", texts[i - 1]):
                found[num] = i + offset
                start = i
                break
    return found


def main() -> None:
    make_crops()
    (HERE / "cover_out.pdf").unlink(missing_ok=True)
    render(HERE / "cover.html", HERE / "cover_out.pdf", header=False)
    html = assemble()
    (HERE / "body.html").write_text(html, encoding="utf-8")
    render(HERE / "body.html", HERE / "body_out.pdf", header=True)
    pages = find_pages(HERE / "body_out.pdf", html, offset=0)
    print("içindekiler:", pages)
    html = assemble(pages)
    (HERE / "body.html").write_text(html, encoding="utf-8")
    render(HERE / "body.html", HERE / "body_out.pdf", header=True)
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    for f in ("cover_out.pdf", "body_out.pdf"):
        for page in PdfReader(str(HERE / f)).pages:
            w.add_page(page)
    w.add_metadata({"/Title": "BasinShift — Kullanım ve Teknik Kılavuz (Sürüm 3.1)", "/Author": "BasinShift ekibi",
                    "/Subject": "NASA Space Apps Challenge 2026 · Field Shift · Konya"})
    with open(OUT, "wb") as fh:
        w.write(fh)
    print("yazıldı:", OUT, OUT.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
