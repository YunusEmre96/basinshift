"""Plan arama, kartların seçimi ve tarla bölme (portföy) karışımları.

Akış:
    1. Havzanın ürünlerinden 4 yıllık tüm sıralamalar (Konya: 13 ürün, çok yıllık yonca hariç 12⁴ = 20.736)
    2. Çiftçi kısıtları: kuru tarıma uygunluk, ekipman, sözleşme, alıcı
    3. Kural paketi (yasal) → yalnızca YEŞİL planlar kartlara aday
    4. Stres testi + toprak skorları (FieldContext.evaluate)
    5. Yem alt sınırı
    6. Pareto cephesi (gelir ↑, kötü dönem geliri ↑, su ↓, toprak ↑, [yem ↑])
    7. Kartlar:
        💰 Kâr    — cephedeki en yüksek ortalama brüt kâr
        💧 Akifer — kârı en iyi planın en az %50'si olan, kötü dönemde zarar etmeyen ve
                    yılların en fazla %30'unda zarar eden planlar içinde en az su
                    (kuru tarımda: 🌵 Kuraklığa dayanıklı — en yüksek kötü dönem geliri)
        ⚖️ Denge  — çiftçinin öncelik ağırlıklarıyla en yüksek skor; tek planlar ve
                    tarla bölme karışımları birlikte yarışır
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..engine.field import FieldContext
from ..engine.metrics import cvar
from .pareto import pareto_mask

OBJECTIVES = ("mean_margin", "cvar5", "water_mean", "soil", "forage")
MINIMIZE = {"water_mean"}
DEFAULT_WEIGHTS = {"income": 3.0, "risk": 3.0, "water": 3.0, "soil": 2.0, "forage": 0.0}
WEIGHT_TO_OBJ = {"income": "mean_margin", "risk": "cvar5", "water": "water_mean", "soil": "soil", "forage": "forage"}
MIX_SHARES = (0.3, 0.5, 0.7)
MIX_CANDIDATES = 25
AQUIFER_MAX_LOSS_PROB = 0.3


class NoFeasiblePlan(ValueError):
    """Kurallara ve çiftçinin kısıtlarına uyan plan yok (kullanıcı kısıt gevşetmeli)."""


@dataclass
class Constraints:
    available_equipment: set[str] | None = None     # None = tüm ekipman var
    contracts: set[str] | None = None               # sözleşmesi olan ürünler (None = hepsi)
    no_buyer: set[str] = field(default_factory=set) # alıcısı olmayan ürünler
    excluded: set[str] = field(default_factory=set) # çiftçinin istemediği ürünler
    min_forage: float = 0.0                         # kg KM/da/yıl
    respect_breaks: bool = True                     # hastalık/zararlı ara verme sürelerine uy (tavsiye)
    include_perennials: bool = False                # yonca gibi çok yıllıklar tek yıl modellendiği için varsayılan dışı


@dataclass
class PlanOption:
    key: str                                        # "profit" | "aquifer" | "balance" | "current"
    parts: list[tuple[tuple[str, ...], float]]      # [(plan, pay)], tek plan → [(plan, 1.0)]
    metrics: dict
    detail: dict

    @property
    def is_mix(self) -> bool:
        return len(self.parts) > 1

    @property
    def main_plan(self) -> tuple[str, ...]:
        return max(self.parts, key=lambda x: x[1])[0]


@dataclass
class SearchResult:
    table: pd.DataFrame          # tüm değerlendirilen planlar
    feasible: pd.DataFrame       # kısıt + yeşil + yem
    pareto: pd.DataFrame
    options: dict[str, PlanOption]
    excluded_crops: dict[str, str]   # ürün → elenme nedeni
    n_total: int


def allowed_crops(ctx: FieldContext, cons: Constraints) -> tuple[list[int], dict[str, str]]:
    keep, why = [], {}
    for i, cid in enumerate(ctx.crop_ids):
        crop, econ = ctx.crops[cid], ctx.econ[cid]
        if not ctx.settings.irrigated and not econ.rainfed_ok:
            why[cid] = "rainfed"
        elif cons.available_equipment is not None and crop.equipment and crop.equipment not in cons.available_equipment:
            why[cid] = "equipment"
        elif crop.contract_required and cons.contracts is not None and cid not in cons.contracts:
            why[cid] = "contract"
        elif cid in cons.no_buyer:
            why[cid] = "no_buyer"
        elif cid in cons.excluded:
            why[cid] = "excluded"
        elif crop.residue_cover_months >= 12 and not cons.include_perennials:
            why[cid] = "perennial"
        else:
            keep.append(i)
    return keep, why


def normalized_scores(df: pd.DataFrame, weights: dict[str, float], ref: pd.DataFrame | None = None) -> np.ndarray:
    ref = df if ref is None else ref
    total = np.zeros(len(df))
    wsum = 0.0
    for wk, w in weights.items():
        if w <= 0:
            continue
        col = WEIGHT_TO_OBJ[wk]
        lo, hi = ref[col].min(), ref[col].max()
        span = hi - lo if hi > lo else 1.0
        z = (df[col].to_numpy() - lo) / span
        if col in MINIMIZE:
            z = 1 - z
        total += w * z
        wsum += w
    return total / wsum if wsum else total


def _single_option(ctx: FieldContext, key: str, row: pd.Series) -> PlanOption:
    plan = tuple(row["plan"])
    det = ctx.detail(list(plan))
    return PlanOption(key, [(plan, 1.0)], dict(det["summary"], **det["soil"]), det)


def mix_detail(details: list[dict], shares: list[float]) -> dict:
    """Tarla bölme: her parçanın (W, N) sonuçları alan payıyla ağırlıklanır."""
    sim = {k: sum(s * d["sim"][k] for d, s in zip(details, shares)) for k in details[0]["sim"]}
    m = sim["margin"]
    summ = {
        "mean_margin": float(m.mean()), "cvar5": float(cvar(m.mean(axis=1), 0.05)),
        "worst_year": float(m.min()),
        "p10_total": float(np.percentile(m.sum(axis=1), 10)),
        "p50_total": float(np.percentile(m.sum(axis=1), 50)),
        "p90_total": float(np.percentile(m.sum(axis=1), 90)),
        "water_mean": float(sim["water_m3"].mean()), "water_total": float(sim["water_m3"].sum(axis=1).mean()),
        "water_p90": float(np.percentile(sim["water_m3"], 90)),
        "yield_ratio": float(sim["yield_ratio"].mean()), "support_mean": float(sim["support"].mean()),
        "loss_prob": float((m < 0).mean()),
    }
    soil = {k: float(sum(s * d["soil"][k] for d, s in zip(details, shares))) for k in details[0]["soil"]}
    status_rank = {"green": 0, "yellow": 1, "red": 2}
    status = max((d["status"] for d in details), key=lambda x: status_rank[x])
    return {"plan": [d["plan"] for d in details], "shares": shares, "summary": summ, "soil": soil,
            "status": status, "sim": sim, "window_start_years": details[0]["window_start_years"],
            "parts": details}


def search(ctx: FieldContext, cons: Constraints | None = None, weights: dict[str, float] | None = None,
           current_plan: list[str] | None = None, allow_mixes: bool = True) -> SearchResult:
    cons = cons or Constraints()
    weights = {**DEFAULT_WEIGHTS, **(weights or {})}
    keep, excluded = allowed_crops(ctx, cons)
    if not keep:
        raise NoFeasiblePlan("Kısıtlar sonrası hiç ürün kalmadı")
    n = ctx.settings.horizon
    plans = np.array(list(itertools.product(keep, repeat=n)), dtype=int)
    table = ctx.evaluate(plans)
    ok = (table["status"] == "green") & (table["forage"] >= cons.min_forage)
    if cons.respect_breaks:
        ok &= table["gap_cnt"] == 0
    feasible = table[ok].copy()
    if feasible.empty:
        raise NoFeasiblePlan("Kurallara ve kısıtlara uyan plan bulunamadı; kısıtları gevşetin")

    obj = np.column_stack([
        -feasible[c].to_numpy() if c in MINIMIZE else feasible[c].to_numpy()
        for c in OBJECTIVES if c != "forage" or weights.get("forage", 0) > 0
    ])
    pmask = pareto_mask(obj)
    pareto = feasible[pmask].copy()
    pareto["score"] = normalized_scores(pareto, weights, feasible)

    options: dict[str, PlanOption] = {}
    best_profit = pareto.loc[pareto["mean_margin"].idxmax()]
    options["profit"] = _single_option(ctx, "profit", best_profit)

    floor = 0.5 * best_profit["mean_margin"] if best_profit["mean_margin"] > 0 else best_profit["mean_margin"] - 1
    others = pareto[pareto["plan"] != best_profit["plan"]]
    # Savunulabilir olmalı: kötü dönemde zarar etmemeli ve yılların en fazla %30'unda zarar
    cand = others[(others["mean_margin"] >= floor) & (others["cvar5"] >= 0) & (others["loss_prob"] <= AQUIFER_MAX_LOSS_PROB)]
    if cand.empty:
        cand = others[others["mean_margin"] >= floor]
    if cand.empty:
        cand = others
    if cand.empty:
        cand = pareto
    # Sulu tarımda en az su; kuru tarımda (su çekimi yok) kötü dönem geliri en yüksek plan
    aq = cand.loc[cand["water_mean"].idxmin()] if ctx.settings.irrigated else cand.loc[cand["cvar5"].idxmax()]
    options["aquifer"] = _single_option(ctx, "aquifer", aq)

    used = {tuple(best_profit["plan"]), tuple(aq["plan"])}
    singles = pareto[~pareto["plan"].isin(used)].sort_values("score", ascending=False)
    if singles.empty:
        singles = pareto.sort_values("score", ascending=False)
    best_single = singles.iloc[0]
    balance = _single_option(ctx, "balance", best_single)

    if allow_mixes and len(pareto) >= 2:
        top = pareto.sort_values("score", ascending=False).head(MIX_CANDIDATES)
        details = {tuple(p): ctx.detail(list(p)) for p in top["plan"]}
        rows = []
        for (p1, d1), (p2, d2) in itertools.combinations(details.items(), 2):
            for a in MIX_SHARES:
                md = mix_detail([d1, d2], [a, 1 - a])
                rows.append({"parts": ((p1, a), (p2, 1 - a)), **md["summary"], **md["soil"], "_md": md})
        if rows:
            mixes = pd.DataFrame(rows)
            pool = pd.concat([feasible, mixes], ignore_index=True)
            mixes["score"] = normalized_scores(mixes, weights, pool)
            single_score = normalized_scores(pd.DataFrame([best_single]), weights, pool)[0]
            best_mix = mixes.loc[mixes["score"].idxmax()]
            if best_mix["score"] > single_score + 0.01:
                md = best_mix["_md"]
                balance = PlanOption("balance", [tuple(x) for x in best_mix["parts"]],
                                     dict(md["summary"], **md["soil"]), md)
    options["balance"] = balance

    if current_plan:
        det = ctx.detail(list(current_plan))
        options["current"] = PlanOption("current", [(tuple(current_plan), 1.0)], dict(det["summary"], **det["soil"]), det)

    return SearchResult(table, feasible, pareto, options, excluded, len(plans))
