"""'Neden bu plan?' paneli — NASA brifindeki beş soru:

    1. Neden önerildi?
    2. Hangi kanıta dayanıyor?
    3. Faydası ne?
    4. Hangi bilgiler eksik (bilgi boşlukları)?
    5. Hangi riskler yerel olarak (çiftçi / ziraat mühendisi) incelenmeli?

Metinler hesap sonuçlarından HAZIR ŞABLONLARLA üretilir; dil modeli
kullanılmaz, böylece her rakamın kaynağı izlenebilir.
"""
from __future__ import annotations

from ..data.hub import Provenance
from ..engine.field import FieldContext
from ..optimizer.search import PlanOption
from ..textutil import loc
from .fmt import money, num, water

CARD_GOAL = {
    "tr": {
        "profit": "kurallara uyarak en yüksek ortalama brüt kârı sağladığı",
        "aquifer": "kârı makul düzeyde tutarken (en iyi planın en az yarısı) en az sulama suyunu gerektirdiği",
        "aquifer_rainfed": "kuru tarımda kötü dönemlerde en yüksek geliri koruduğu",
        "balance": "seçtiğiniz önceliklere göre gelir, risk, su ve toprak arasında en iyi dengeyi kurduğu",
        "current": "sizin mevcut planınız olduğu",
    },
    "en": {
        "profit": "it delivers the highest average gross margin while complying with the rules",
        "aquifer": "it needs the least irrigation water while keeping at least half the best plan's margin",
        "aquifer_rainfed": "it best protects income in bad periods under rainfed conditions",
        "balance": "it best balances income, risk, water and soil for your chosen priorities",
        "current": "it is your current plan",
    },
}


def _crops_in(option: PlanOption) -> list[str]:
    seen = []
    for plan, _ in option.parts:
        for c in plan:
            if c not in seen:
                seen.append(c)
    return seen


def explain(option: PlanOption, current: PlanOption | None, ctx: FieldContext,
            provenance: dict[str, Provenance], lang: str = "tr", unit: str = "da") -> dict[str, list[str]]:
    tr = lang == "tr"
    sym = ctx.basin.currency_symbol
    m = option.metrics
    crops = ctx.crops
    out = {"why": [], "evidence": [], "benefits": [], "gaps": [], "local_risks": []}

    # 1) Neden
    key = option.key
    if key == "aquifer" and not ctx.settings.irrigated:
        key = "aquifer_rainfed"
    goal = CARD_GOAL[lang][key]
    out["why"].append(("Bu plan, " if tr else "Suggested because ") + goal + ("." if not tr else " için önerildi."))
    if option.is_mix:
        out["why"].append(
            "Tarla ikiye bölünerek farklı ürünler aynı yıl birlikte ekilir; ürünler kötü yıllara farklı tepki verdiği için gelir dalgalanması azalır."
            if tr else
            "The field is split so different crops grow in the same year; they react differently to bad years, smoothing income."
        )
    if current is not None and key != "current":
        c = current.metrics
        dw = m["water_mean"] - c["water_mean"]
        dm = m["mean_margin"] - c["mean_margin"]
        dr = m["cvar5"] - c["cvar5"]
        if c["water_mean"] > 0 and abs(dw) >= 1:
            pct = dw / c["water_mean"] * 100
            out["why"].append(
                (f"Mevcut planınıza göre yıllık sulama suyu {water(abs(dw), unit, lang)} "
                 f"({'az' if dw < 0 else 'fazla'}, %{abs(pct):.0f}).") if tr else
                (f"Versus your current plan, yearly irrigation is {water(abs(dw), unit, lang)} "
                 f"{'lower' if dw < 0 else 'higher'} ({abs(pct):.0f}%).")
            )
        out["why"].append(
            (f"Ortalama brüt kâr farkı: {'+' if dm >= 0 else '−'}{money(abs(dm), sym, unit, lang)} / yıl; "
             f"kötü dönem geliri farkı: {'+' if dr >= 0 else '−'}{money(abs(dr), sym, unit, lang)} / yıl.") if tr else
            (f"Average gross margin difference: {'+' if dm >= 0 else '−'}{money(abs(dm), sym, unit, lang)}/yr; "
             f"bad-period income difference: {'+' if dr >= 0 else '−'}{money(abs(dr), sym, unit, lang)}/yr.")
        )
        if current.detail["status"] != "green" and option.detail["status"] == "green":
            out["why"].append(
                "Mevcut planınız su kısıtı / münavebe kuralını ihlal ediyor; bu plan kurala uyuyor ve destek kaybını önlüyor."
                if tr else
                "Your current plan breaks the rotation / water rules; this plan complies and avoids losing support."
            )

    # 2) Kanıt
    cp = provenance.get("climate_daily")
    years = ctx.table.years
    n_windows = len(years) - ctx.settings.horizon + 1
    clim_label = cp.label(lang) if cp else "?"
    out["evidence"].append(
        (f"İklim: {cp.product_text(lang) if cp else ''} — kaynak: {clim_label}; {years[0]}–{years[-1]} hasat yılları, "
         f"{n_windows} farklı 4 yıllık dönemde yeniden oynatıldı.") if tr else
        (f"Climate: {cp.product_text(lang) if cp else ''} — source: {clim_label}; harvest years {years[0]}–{years[-1]}, "
         f"replayed over {n_windows} different 4-year periods.")
    )
    out["evidence"].append(
        "Su: FAO-56 Penman-Monteith ET0 ve günlük kök bölgesi su dengesi; verim: FAO-33 verim tepki faktörü (Ky)."
        if tr else
        "Water: FAO-56 Penman-Monteith ET0 and daily root-zone water balance; yield: FAO-33 yield response factor (Ky)."
    )
    sm = provenance.get("soil_moisture")
    out["evidence"].append(
        (f"Ekimdeki toprak nemi: {ctx.table.wetness_source}"
         + (f" (SMAP kaynağı: {sm.label(lang)})" if sm and sm.actual else "") + ".") if tr else
        (f"Soil moisture at planting: {loc(ctx.table.wetness_source, lang)}"
         + (f" (SMAP source: {sm.label(lang)})" if sm and sm.actual else "") + ".")
    )
    out["evidence"].append(
        ("Kurallar: " if tr else "Rules: ") + "; ".join(p.name(lang) for p in ctx.packs)
    )

    # 3) Fayda
    soil = option.detail["soil"]
    legumes = [c for c in _crops_in(option) if crops[c].n_fixing]
    if legumes:
        out["benefits"].append(
            (f"Azot bağlayan ürünler ({', '.join(crops[c].name(lang) for c in legumes)}) sonraki ürünün gübre ihtiyacını azaltır "
             f"(azot skoru {soil['nitrogen']:.0f}/100).") if tr else
            (f"Nitrogen-fixing crops ({', '.join(crops[c].name(lang) for c in legumes)}) cut fertiliser needs "
             f"(nitrogen score {soil['nitrogen']:.0f}/100).")
        )
    deep = [c for c in _crops_in(option) if crops[c].deep_rooted and not crops[c].residue_cover_months >= 12]
    if deep:
        out["benefits"].append(
            (f"Derin köklü ürünler ({', '.join(crops[c].name(lang) for c in deep)}) alt katmanlardaki suyu kullanır.") if tr else
            (f"Deep-rooted crops ({', '.join(crops[c].name(lang) for c in deep)}) use deeper soil water.")
        )
    out["benefits"].append(
        (f"Toprak sağlığı {soil['soil']:.0f}/100 (azot {soil['nitrogen']:.0f}, organik madde {soil['organic_matter']:.0f}, "
         f"erozyon/çıplak toprak {soil['erosion']:.0f}, zararlı döngüsü {soil['pest_cycle']:.0f}); "
         f"yılda ortalama {soil['bare_months']:.1f} ay çıplak toprak.") if tr else
        (f"Soil health {soil['soil']:.0f}/100 (nitrogen {soil['nitrogen']:.0f}, organic matter {soil['organic_matter']:.0f}, "
         f"erosion/bare soil {soil['erosion']:.0f}, pest cycle {soil['pest_cycle']:.0f}); "
         f"{soil['bare_months']:.1f} bare months per year on average.")
    )
    if m.get("support_mean", 0) > 0:
        out["benefits"].append(
            (f"Tahmini destek ortalama {money(m['support_mean'], sym, unit, lang)} / yıl.") if tr else
            (f"Estimated support averages {money(m['support_mean'], sym, unit, lang)}/yr.")
        )
    if soil.get("forage", 0) > 0:
        out["benefits"].append(
            (f"Yem üretimi: yılda ortalama {num(soil['forage'], lang)} kg kuru madde/da.") if tr else
            (f"Forage: about {num(soil['forage'], lang)} kg dry matter per decare per year.")
        )

    # 4) Bilgi boşlukları
    defaults = [ds for ds, p in provenance.items() if p.is_default]
    if defaults:
        out["gaps"].append(
            (f"Şu veri setleri alınamadı, varsayılan değer kullanıldı: {', '.join(defaults)}.") if tr else
            (f"These datasets were unavailable and defaults were used: {', '.join(defaults)}.")
        )
    if any(p.is_synthetic for p in provenance.values()):
        out["gaps"].append(
            "Bu sonuçlar SENTETİK demo verisiyle üretildi; gerçek NASA verisi bağlanınca yeniden hesaplanmalı."
            if tr else
            "These results use SYNTHETIC demo data; recompute once real NASA data is connected."
        )
    out["gaps"].append(
        "Ürün fiyatları ve maliyetler 2026 varsayımıdır; gelir tahmini fiyat değişimine en duyarlı kalemdir."
        if tr else
        "Crop prices and costs are 2026 assumptions; income is most sensitive to price changes."
    )
    out["gaps"].append(
        "Önceki ürünün verime etkisi (ör. baklagil sonrası buğday) literatür ortalamasıdır; yerel deneme verisiyle kalibre edilmeli."
        if tr else
        "Previous-crop effects (e.g. wheat after legumes) are literature averages; calibrate with local trials."
    )
    out["gaps"].append(
        (f"İklim verisi {cp.resolution_text(lang) if cp else ''} çözünürlükte; tarla içi farklılıkları (toprak, eğim) göstermez.") if tr else
        (f"Climate data is at {cp.resolution_text(lang) if cp else ''}; it does not capture within-field differences.")
    )
    for pk in ctx.packs:
        if pk.status(lang):
            out["gaps"].append(f"{pk.name(lang)}: {pk.status(lang)}")

    # 5) Yerel olarak incelenmesi gereken riskler
    for c in _crops_in(option):
        crop = crops[c]
        out["local_risks"].append(f"{crop.name(lang)}: {crop.local_risks(lang)}")
        if crop.contract_required:
            out["local_risks"].append(
                f"{crop.name(lang)}: " + ("sözleşme/kota durumunu fabrikayla teyit edin." if tr else "confirm contract/quota with the processor.")
            )
    out["local_risks"].append(
        "Ekim tarihleri ve çeşit seçimi yerel ziraat mühendisiyle birlikte belirlenmelidir."
        if tr else
        "Sowing dates and varieties should be chosen with a local agronomist."
    )
    return out
