"""Biçimlendirme yardımcıları (para, alan birimi, plan metni)."""
from __future__ import annotations

from ..knowledge.tables import Crop

AREA = {"da": (1.0, "da"), "ha": (10.0, "ha")}


def area_factor(unit: str) -> float:
    return AREA.get(unit, AREA["da"])[0]


def money(x: float, symbol: str, unit: str = "da", lang: str = "tr") -> str:
    v = x * area_factor(unit)
    s = f"{v:,.0f}"
    if lang == "tr":
        s = s.replace(",", ".")
    return f"{s} {symbol}/{unit}"


def water(m3_per_da: float, unit: str = "da", lang: str = "tr") -> str:
    v = m3_per_da * area_factor(unit)
    s = f"{v:,.0f}"
    if lang == "tr":
        s = s.replace(",", ".")
    return f"{s} m³/{unit}"


def num(x: float, lang: str = "tr", digits: int = 0) -> str:
    s = f"{x:,.{digits}f}"
    if lang == "tr":
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def plan_text(plan, crops: dict[str, Crop], lang: str = "tr") -> str:
    return " → ".join(crops[c].name(lang) for c in plan)


def option_text(parts, crops: dict[str, Crop], lang: str = "tr") -> str:
    if len(parts) == 1:
        return plan_text(parts[0][0], crops, lang)
    return "  +  ".join(f"%{share*100:.0f} [{plan_text(p, crops, lang)}]" if lang == "tr"
                        else f"{share*100:.0f}% [{plan_text(p, crops, lang)}]" for p, share in parts)


def merged_year(parts, i: int) -> list[tuple[str, float]]:
    """Karışımda i. yıl: aynı ürünü birleştirip [(ürün, pay)] döner (büyükten küçüğe)."""
    acc: dict[str, float] = {}
    for p, s in parts:
        acc[p[i]] = acc.get(p[i], 0.0) + s
    return sorted(acc.items(), key=lambda x: -x[1])


def year_cells(parts, crops: dict[str, Crop], lang: str = "tr") -> list[str]:
    """Her plan yılı için hücre metni (karışımlarda payları gösterir)."""
    n = len(parts[0][0])
    out = []
    for i in range(n):
        if len(parts) == 1:
            out.append(crops[parts[0][0][i]].name(lang))
        else:
            m = merged_year(parts, i)
            if len(m) == 1:
                out.append(crops[m[0][0]].name(lang))
            else:
                out.append(" + ".join(f"%{s*100:.0f} {crops[c].name(lang)}" if lang == "tr"
                                      else f"{s*100:.0f}% {crops[c].name(lang)}" for c, s in m))
    return out
