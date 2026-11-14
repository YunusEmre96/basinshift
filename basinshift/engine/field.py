"""Tarla modeli ve stres testi.

Bir 4 yıllık plan, geçmişin her ardışık 4 yıllık penceresinde (1982–85,
1983–86, …) "yeniden oynatılır". Böylece kurak yılların art arda gelmesi
gibi gerçek diziler korunur. Her (plan, pencere, yıl) için verim, gelir,
maliyet, sulama suyu ve destek hesaplanır.

Verim (FAO-33):
    1 − Ya/Ym = Ky · (1 − ETa/ETc)
    Ya = Ym · (FAO-33 oranı) · iklim stresi çarpanı · önceki ürün çarpanı
Brüt kâr (para/da/yıl):
    Ya · fiyat − değişken maliyet · (1 − azot tasarrufu) − sulama m³ · su maliyeti + destek
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..data.basins import Basin, Site
from ..knowledge.rules import RulePack, evaluate_plans, support_matrix, water_cap
from ..knowledge.tables import Crop, Economics
from .metrics import cvar
from .rotation import rotation_matrices
from .soil import COVER_CROP, CropAttrArrays, crop_attr_arrays, soil_scores
from .water import IRRIGATION_EFFICIENCY, CropYearTable

CHUNK = 2000


@dataclass
class FieldSettings:
    irrigated: bool
    irrigation_method: str            # drip | sprinkler | surface | none
    water_restricted: bool
    farmer_water_cap_m3: float | None  # çiftçinin kullanılabilir suyu (m³/da/yıl), None = sınırsız
    water_cost_per_m3: float
    history: list[str]                # eski → yeni, ör. ["sugar_beet", "maize_grain"]
    plan_start_year: int
    horizon: int = 4
    cover_crop: bool = False

    @property
    def efficiency(self) -> float:
        return IRRIGATION_EFFICIENCY.get(self.irrigation_method, 0.75) if self.irrigated else 1.0

    @property
    def plan_years(self) -> list[int]:
        return list(range(self.plan_start_year, self.plan_start_year + self.horizon))


@dataclass
class FieldContext:
    basin: Basin
    site: Site
    crops: dict[str, Crop]
    econ: dict[str, Economics]
    crop_ids: list[str]
    table: CropYearTable
    packs: list[RulePack]
    settings: FieldSettings
    slope_deg: float
    attrs: CropAttrArrays = field(init=False)
    rot_mult: np.ndarray = field(init=False)
    n_credit: np.ndarray = field(init=False)
    rot_conf: np.ndarray = field(init=False)
    cap_net_mm: float = field(init=False)
    rule_cap_m3: float | None = field(init=False)
    #: Bu tarlanın verisinin kaynak kaydı (pipeline.build_context doldurur)
    provenance: dict = field(default_factory=dict)

    def __post_init__(self):
        self.attrs = crop_attr_arrays(self.crop_ids, self.crops, self.econ, self.basin)
        self.rot_mult, self.n_credit, self.rot_conf = rotation_matrices(self.crop_ids, self.crops)
        s = self.settings
        self.rule_cap_m3 = water_cap(self.packs, s.irrigated, s.water_restricted)
        caps = [c for c in (s.farmer_water_cap_m3, self.rule_cap_m3) if c is not None]
        cap_gross = min(caps) if caps else np.inf
        self.cap_net_mm = cap_gross * s.efficiency if s.irrigated else 0.0
        ids = self.crop_ids
        self.ym = np.array([self.econ[c].ym_kg_da for c in ids])
        self.price = np.array([self.econ[c].price_per_kg for c in ids])
        cost = np.array([self.econ[c].var_cost_per_da for c in ids])
        rf = np.array([self.econ[c].rainfed_cost_factor for c in ids])
        self.cost = cost if s.irrigated else cost * rf
        self.ky = np.array([self.crops[c].ky for c in ids])
        self.is_fallow = np.array([self.crops[c].is_fallow for c in ids])
        wheat_cost = self.econ["wheat"].var_cost_per_da if "wheat" in self.econ else float(np.median(cost))
        self.cover_cost = COVER_CROP["cost_share_of_wheat"] * wheat_cost

    # ------------------------------------------------------------------
    def idx(self, plan: list[str]) -> np.ndarray:
        return np.array([self.crop_ids.index(c) for c in plan], dtype=int)

    @property
    def history_idx(self) -> list[int]:
        return [self.crop_ids.index(c) for c in self.settings.history if c in self.crop_ids]

    def windows(self) -> np.ndarray:
        n = self.settings.horizon
        y = len(self.table.years)
        return np.arange(y - n + 1)[:, None] + np.arange(n)[None, :]   # (W, N) yıl indeksleri

    def rules(self, plans: np.ndarray) -> dict:
        s = self.settings
        return evaluate_plans(plans, self.history_idx, self.crop_ids, self.crops, self.packs,
                              s.irrigated, s.water_restricted)

    def cover_mask(self, plans: np.ndarray) -> np.ndarray:
        if not self.settings.cover_crop:
            return np.zeros(plans.shape, dtype=bool)
        return self.attrs.cover_ok[plans] > 0

    # ------------------------------------------------------------------
    def simulate(self, plans: np.ndarray, supports: np.ndarray, cover: np.ndarray | None = None) -> dict:
        """Tam ayrıntılı simülasyon: her dizi (P, W, N)."""
        t = self.table
        s = self.settings
        win = self.windows()                                   # (W, N)
        c = plans[:, None, :]                                  # (P, 1, N)
        yi = win[None, :, :]                                   # (1, W, N)
        hist = self.history_idx
        unknown = len(self.crop_ids)
        prev = np.concatenate(
            [np.full((plans.shape[0], 1), hist[-1] if hist else unknown), plans[:, :-1]], axis=1
        )[:, None, :]                                          # (P, 1, N)

        etc = t.etc[c, yi]
        eta_rf = t.eta_rf[c, yi]
        ir_full = t.ir_net[c, yi]
        stress = t.stress_mult[c, yi]

        # Nadas sonrası depolanan su (önceki yıl nadas ise) — %80'i ürüne yarar
        prev_year = np.maximum(yi - 1, 0)
        prev_is_fallow = np.zeros(prev.shape, bool)
        valid_prev = prev < unknown
        prev_is_fallow[valid_prev] = self.is_fallow[prev[valid_prev]]
        extra = np.where(prev_is_fallow, t.fallow_store[prev_year], 0.0)
        # Örtü bitkisi (önceki yıl) sonraki ürünün başlangıç suyunu azaltır
        cov_cost = 0.0
        if cover is not None and cover.any():
            prev_cover = np.concatenate([np.zeros((plans.shape[0], 1), bool), cover[:, :-1]], axis=1)[:, None, :]
            extra = extra - np.where(prev_cover, COVER_CROP["water_mm"], 0.0)
            cov_cost = np.where(cover[:, None, :], self.cover_cost, 0.0)
        extra = np.minimum(0.8 * extra, t.taw[c])
        eta_rf = np.clip(eta_rf + extra, 0, etc)
        need = np.clip(ir_full - extra, 0, None)

        if s.irrigated:
            applied = np.minimum(need, self.cap_net_mm)
            gross = applied / s.efficiency
        else:
            applied = np.zeros_like(need)
            gross = applied
        frac = np.divide(applied, need, out=np.zeros_like(need), where=need > 0)
        eta = eta_rf + (etc - eta_rf) * frac
        ratio = np.divide(eta, etc, out=np.ones_like(etc), where=etc > 0)
        water_yr = np.clip(1 - self.ky[c] * (1 - ratio), 0, 1)
        rot = self.rot_mult[prev, c]
        yield_ratio = water_yr * stress * rot
        yld = self.ym[c] * yield_ratio
        revenue = yld * self.price[c]
        cost = self.cost[c] * (1 - self.n_credit[prev, c]) + gross * s.water_cost_per_m3 + cov_cost
        support = np.broadcast_to(supports[:, None, :], revenue.shape)
        margin = revenue - cost + support
        return {
            "margin": margin, "revenue": revenue, "cost": cost, "support": support, "water_m3": gross,
            "yield": yld, "yield_ratio": yield_ratio, "water_ratio": water_yr, "stress": stress,
            "deficit_mm": need - applied,
        }

    def summarize(self, sim: dict) -> dict[str, np.ndarray]:
        m = sim["margin"]
        p = m.shape[0]
        flat = m.reshape(p, -1)
        totals = m.sum(axis=2)                                  # (P, W)
        w = sim["water_m3"]
        window_mean = m.mean(axis=2)                            # (P, W) dönemin yıllık ortalaması
        return {
            "mean_margin": flat.mean(axis=1),
            # En kötü %5'lik 4 yıllık dönemlerde yıllık ortalama brüt kâr. Yıl yerine dönem
            # kullanılır; böylece planlı nadas yılı "kötü yıl" sayılmaz.
            "cvar5": cvar(window_mean, 0.05),
            "worst_year": flat.min(axis=1),
            "p10_total": np.percentile(totals, 10, axis=1),
            "p50_total": np.percentile(totals, 50, axis=1),
            "p90_total": np.percentile(totals, 90, axis=1),
            "water_mean": w.reshape(p, -1).mean(axis=1),
            "water_total": w.sum(axis=2).mean(axis=1),
            "water_p90": np.percentile(w.reshape(p, -1), 90, axis=1),
            "yield_ratio": sim["yield_ratio"].reshape(p, -1).mean(axis=1),
            "support_mean": sim["support"].reshape(p, -1).mean(axis=1),
            "loss_prob": (flat < 0).mean(axis=1),
        }

    def evaluate(self, plans: np.ndarray) -> pd.DataFrame:
        """Binlerce plan: kurallar + stres testi + toprak; özet tablo döner."""
        rows = []
        for i in range(0, len(plans), CHUNK):
            chunk = plans[i:i + CHUNK]
            r = self.rules(chunk)
            sup = support_matrix(chunk, r["legal_viol"], self.crop_ids, self.packs,
                                 self.settings.irrigated, self.settings.water_restricted)
            cover = self.cover_mask(chunk)
            sim = self.simulate(chunk, sup, cover if cover.any() else None)
            summ = self.summarize(sim)
            soil = soil_scores(chunk, self.attrs, r["gap_viol"], r["family_viol"], self.slope_deg,
                               cover if cover.any() else None)
            df = pd.DataFrame({**summ, **{k: v for k, v in soil.items()}})
            df["status"] = r["status"]
            df["advisory_cnt"] = r["advisory_cnt"]
            df["gap_cnt"] = r["gap_viol"].sum(axis=1)
            df["plan_idx"] = list(map(tuple, chunk))
            rows.append(df)
        out = pd.concat(rows, ignore_index=True)
        out["plan"] = out["plan_idx"].map(lambda t: tuple(self.crop_ids[j] for j in t))
        return out

    def detail(self, plan: list[str]) -> dict:
        """Tek plan için ayrıntılı çıktı (grafikler, açıklama, karne)."""
        arr = self.idx(plan)[None, :]
        r = self.rules(arr)
        sup = support_matrix(arr, r["legal_viol"], self.crop_ids, self.packs,
                             self.settings.irrigated, self.settings.water_restricted)
        cover = self.cover_mask(arr)
        sim = self.simulate(arr, sup, cover if cover.any() else None)
        summ = {k: float(v[0]) for k, v in self.summarize(sim).items()}
        soil = {k: float(v[0]) for k, v in soil_scores(arr, self.attrs, r["gap_viol"], r["family_viol"],
                                                       self.slope_deg, cover if cover.any() else None).items()}
        per_slot = {
            k: sim[k][0] for k in ("margin", "water_m3", "yield", "yield_ratio", "support", "stress", "deficit_mm")
        }
        return {
            "plan": list(plan), "summary": summ, "soil": soil, "status": str(r["status"][0]),
            "legal_viol": r["legal_viol"][0], "sim": per_slot, "supports": sup[0],
            "window_start_years": self.table.years[self.windows()[:, 0]],
        }
