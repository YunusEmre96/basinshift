"""Havza modeli.

Soru: "Bir çiftçi için doğru olan, bin çiftçi aynısını yapınca ne olur?"

Havza, temsili çiftlik tipleriyle (tables/farm_types.csv — SENTETİK, gerçek
uygulamada ÇKS/kooperatif verisiyle değişir) modellenir. Her tipin her ürün
için ortalama verimi, suyu ve kârı, tarla modelinin stres testinden gelir.

Üç senaryo karşılaştırılır:
    1. Mevcut desen        — çiftlik tiplerinin bugünkü ürün payları, referans fiyatlar
    2. Koordinasyonsuz     — her tip kendi başına GEÇEN YILIN fiyatına göre en kârlı
                              deseni seçer (örümcek ağı/cobweb döngüsü); havza su
                              bütçesini kimse dikkate almaz
    3. Koordineli          — havza ölçeğinde doğrusal programlama (HiGHS):
                              en yüksek toplam brüt kâr, şu kısıtlarla:
                                * sürdürülebilir su bütçesi
                                * yasal rotasyon kuralları (kararlı durumda grup payı ≤ max/pencere)
                                * pazar sınırları (fiyat %15'ten fazla düşmeden emilebilecek miktar)
                                * havzanın yem ihtiyacı (mevcut üretimin %90'ı)
                                * tek ürüne en fazla pay (çeşitlendirme)

Fiyat tepkisi (sabit esneklikli talep):  p = p_ref · (Q / Q_ref)^(1/ε)
ε (talep esnekliği) basin_economics.csv'de; ulusal pazarda satılan buğday
için büyük (|ε| yüksek → havza fiyatı az etkiler), yerel/niş ürünlerde küçük.

Çıktılar:
    * koordinasyonsuzluğun bedeli (gelir ve su farkı)
    * suyun gölge fiyatı (su kısıtının dual değeri): 1 m³ ek suyun havzaya değeri
    * su bütçesine göre gölge fiyat eğrisi
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from ..data.basins import Basin
from ..data.hub import DataHub
from ..engine.field import FieldContext, FieldSettings
from ..engine.pipeline import SiteData, build_context, load_site_data
from ..engine.scenarios import Scenario
from ..textutil import bi
from ..knowledge.rules import support_matrix
from ..knowledge.tables import load_farm_types_df

# Yerel arz fazlası fiyatı düşürür; yerel arz azaldığında ise ulusal/uluslararası pazar
# (ithalat, TMO, fabrika alım fiyatı) fiyat artışını sınırlar → asimetrik sınır.
PRICE_CLIP = (0.5, 1.2)
ADJUSTMENT_RATE = 0.3      # çiftçiler her yıl alanlarının ~%30'unu "en kârlı" desene kaydırır (kısmi uyum)
MARKET_PRICE_DROP = 0.15
NEW_CROP_MARKET_SHARE = 0.03
FORAGE_KEEP = 0.9
COBWEB_YEARS = 12
COBWEB_BURN_IN = 2


@dataclass
class FarmType:
    id: str
    name_tr: str
    name_en: str
    area_da: float
    irrigated: bool
    irrigation_method: str
    site_id: str
    current: dict[str, float]
    max_share: float

    def name(self, lang: str) -> str:
        return self.name_tr if lang == "tr" else self.name_en


@dataclass
class TypeEconomics:
    """Bir çiftlik tipi için ürün başına ortalama değerler (para/da, kg/da, m³/da)."""
    crop_ids: list[str]
    yield_kg: np.ndarray
    water_m3: np.ndarray
    fixed: np.ndarray          # fiyattan bağımsız kısım: −maliyet − su maliyeti + destek
    forage: np.ndarray
    feasible: np.ndarray       # bool


@dataclass
class BasinResult:
    farm_types: list[FarmType]
    crop_ids: list[str]
    current: np.ndarray            # (T, C) alan da
    coordinated: np.ndarray        # (T, C)
    uncoordinated_last: np.ndarray # (T, C) son yıl deseni
    metrics: pd.DataFrame          # senaryo × gösterge
    price_path: pd.DataFrame       # koordinasyonsuz yıllarda fiyat endeksi (p/p_ref)
    area_path: pd.DataFrame        # koordinasyonsuz yıllarda ürün alanları
    shadow_price_water: float      # para / m³
    water_budget_m3: float
    budget_curve: pd.DataFrame     # su bütçesi oranı → gölge fiyat, gelir
    price_of_anarchy_income: float
    price_of_anarchy_water: float
    currency_symbol: str
    lp_status: str
    notes: list[str] = field(default_factory=list)
    #: çiftlik tipi × senaryo: toplam gelir ve su (kooperatif kazanç paylaşımı için)
    type_table: pd.DataFrame = field(default_factory=pd.DataFrame)


def load_farm_types(basin_id: str) -> list[FarmType]:
    df = load_farm_types_df()
    out = []
    for r in df[df["basin"] == basin_id].to_dict("records"):
        pattern = {}
        for part in str(r["current_pattern"]).split(";"):
            if ":" in part:
                c, v = part.split(":")
                pattern[c.strip()] = float(v)
        tot = sum(pattern.values())
        pattern = {k: v / tot for k, v in pattern.items()}
        out.append(FarmType(r["type_id"], r["name_tr"], r["name_en"], float(r["area_da"]), bool(int(r["irrigated"])),
                            r["irrigation_method"], r["site_id"], pattern, float(r["max_crop_share"])))
    if not out:
        raise KeyError(f"farm_types.csv içinde havza yok: {basin_id}")
    return out


def type_economics(ctx: FieldContext) -> TypeEconomics:
    """Her ürün tek başına (önceki ürün nötr) ekildiğinde geçmiş yılların ortalaması."""
    n = ctx.settings.horizon
    c = len(ctx.crop_ids)
    plans = np.repeat(np.arange(c)[:, None], n, axis=1)
    legal = np.zeros(plans.shape, dtype=bool)
    sup = support_matrix(plans, legal, ctx.crop_ids, ctx.packs, ctx.settings.irrigated, ctx.settings.water_restricted)
    sim = ctx.simulate(plans, sup)
    first = (slice(None), slice(None), 0)
    yld = sim["yield"][first].mean(axis=1)
    water = sim["water_m3"][first].mean(axis=1)
    cost = sim["cost"][first].mean(axis=1)
    support = sim["support"][first].mean(axis=1)
    feasible = np.array([ctx.settings.irrigated or ctx.econ[cid].rainfed_ok for cid in ctx.crop_ids])
    forage = ctx.attrs.forage
    return TypeEconomics(list(ctx.crop_ids), yld, water, support - cost, forage, feasible)


def _price_index(q: np.ndarray, q_ref: np.ndarray, eps: np.ndarray) -> np.ndarray:
    ratio = np.divide(q, q_ref, out=np.ones_like(q), where=q_ref > 0)
    ratio = np.maximum(ratio, 1e-3)
    return np.clip(ratio ** (1.0 / eps), *PRICE_CLIP)


def _restricted_share(ctx: FieldContext) -> tuple[list[int], float] | None:
    """Yasal grup kuralını kararlı durum payına çevirir: 4 yılda en fazla 2 → %50."""
    s = ctx.settings
    for pk in ctx.packs:
        if pk.kind != "legal" or not pk.applies(s.irrigated, s.water_restricted):
            continue
        for r in pk.rules:
            if r["type"] == "group_max_in_window":
                idx = [ctx.crop_ids.index(c) for c in r["crops"] if c in ctx.crop_ids]
                return idx, float(r["max"]) / float(r["window"])
    return None


def _allowed_mask(ctx: FieldContext) -> np.ndarray:
    s = ctx.settings
    allowed = np.ones(len(ctx.crop_ids), dtype=bool)
    for pk in ctx.packs:
        if pk.kind != "legal" or not pk.applies(s.irrigated, s.water_restricted):
            continue
        for r in pk.rules:
            if r["type"] == "allowed_crops":
                allowed &= np.isin(ctx.crop_ids, r["crops"])
    return allowed


def run_basin(hub: DataHub, basin: Basin, scenario: Scenario = Scenario(),
              sustainable_fraction: float | None = None, site_data_cache: dict[str, SiteData] | None = None,
              plan_start_year: int = 2027) -> BasinResult:
    types = load_farm_types(basin.id)
    cache = site_data_cache if site_data_cache is not None else {}
    ctxs: list[FieldContext] = []
    for ft in types:
        site = basin.site(ft.site_id)
        if ft.site_id not in cache:
            cache[ft.site_id] = load_site_data(hub, site, basin)
        st = FieldSettings(ft.irrigated, ft.irrigation_method if ft.irrigated else "none", site.water_restricted,
                           None, basin.water_cost_per_m3, [], plan_start_year)
        ctxs.append(build_context(hub, site, basin, st, scenario, site_data=cache[ft.site_id]))

    crop_ids = ctxs[0].crop_ids
    T, C = len(types), len(crop_ids)
    econ = ctxs[0].econ
    price_ref = np.array([econ[c].price_per_kg for c in crop_ids])
    eps = np.array([econ[c].demand_elasticity for c in crop_ids])
    te = [type_economics(ctx) for ctx in ctxs]
    Y = np.array([t.yield_kg for t in te])          # (T, C)
    Wm = np.array([t.water_m3 for t in te])
    F = np.array([t.fixed for t in te])
    FOR = np.array([t.forage for t in te])
    feas = np.array([t.feasible for t in te]) & np.array([_allowed_mask(ctx) for ctx in ctxs])
    A = np.array([ft.area_da for ft in types])

    cur = np.zeros((T, C))
    for i, ft in enumerate(types):
        for c, share in ft.current.items():
            if c in crop_ids:
                cur[i, crop_ids.index(c)] = share * ft.area_da

    q_cur = (Y * cur).sum(axis=0)
    total_area = A.sum()
    q_floor = NEW_CROP_MARKET_SHARE * total_area * np.where(Y.max(axis=0) > 0, Y.max(axis=0), 0)
    q_ref = np.maximum(q_cur, q_floor)
    water_cur = float((Wm * cur).sum())
    frac = basin.sustainable_water_fraction if sustainable_fraction is None else sustainable_fraction
    budget = frac * water_cur
    forage_need = FORAGE_KEEP * float((FOR * cur).sum())

    def evaluate(x: np.ndarray, prices: np.ndarray | None = None) -> dict:
        q = (Y * x).sum(axis=0)
        if prices is None:
            pidx = _price_index(q, q_ref, eps)
        else:
            pidx = np.divide(prices, price_ref, out=np.ones_like(price_ref), where=price_ref > 0)
        by_type = ((Y * price_ref * pidx + F) * x).sum(axis=1)
        return {"income": float(by_type.sum()), "water": float((Wm * x).sum()), "price_index": pidx, "q": q,
                "type_income": by_type, "type_water": (Wm * x).sum(axis=1)}

    restricted = [_restricted_share(ctx) for ctx in ctxs]

    def solve(margin: np.ndarray, with_basin: bool, water_budget: float | None = None,
              types_subset: list[int] | None = None):
        """margin: (T, C) para/da. Dönen: (x, sonuç, su dual)."""
        ts = types_subset if types_subset is not None else list(range(T))
        var = [(t, c) for t in ts for c in range(C) if feas[t, c]]
        nv = len(var)
        cvec = -np.array([margin[t, c] for t, c in var])
        a_ub, b_ub, a_eq, b_eq, bounds = [], [], [], [], []
        for t, c in var:
            bounds.append((0, types[t].max_share * A[t]))
        for t in ts:                                    # alan eşitliği
            row = np.zeros(nv)
            for k, (tt, _) in enumerate(var):
                if tt == t:
                    row[k] = 1
            a_eq.append(row)
            b_eq.append(A[t])
            rs = restricted[t]
            if rs:                                      # yasal rotasyon (kararlı durum)
                idx, share = rs
                row = np.zeros(nv)
                for k, (tt, cc) in enumerate(var):
                    if tt == t and cc in idx:
                        row[k] = 1
                a_ub.append(row)
                b_ub.append(share * A[t])
        water_row = None
        if with_basin:
            row = np.array([Wm[t, c] for t, c in var])
            water_row = len(a_ub)
            a_ub.append(row)
            b_ub.append(water_budget if water_budget is not None else budget)
            cap_q = q_ref * (1 - MARKET_PRICE_DROP) ** eps     # fiyat %15 düşmeden emilebilen miktar
            for c in range(C):
                row = np.array([Y[t, cc] if cc == c else 0.0 for t, cc in var])
                if row.any():
                    a_ub.append(row)
                    b_ub.append(cap_q[c])
            if forage_need > 0:
                a_ub.append(-np.array([FOR[t, c] for t, c in var]))
                b_ub.append(-forage_need)
        res = linprog(cvec, A_ub=np.array(a_ub) if a_ub else None, b_ub=np.array(b_ub) if b_ub else None,
                      A_eq=np.array(a_eq), b_eq=np.array(b_eq), bounds=bounds, method="highs")
        x = np.zeros((T, C))
        if res.status == 0:
            for k, (t, c) in enumerate(var):
                x[t, c] = res.x[k]
        dual = None
        if water_row is not None and res.status == 0 and res.ineqlin is not None:
            dual = float(-res.ineqlin.marginals[water_row])
        return x, res, dual

    notes = []
    margin_ref = Y * price_ref + F
    coord, res, shadow = solve(margin_ref, True)
    lp_status = res.message if res.status != 0 else "optimal"
    if res.status != 0:
        notes.append(bi("Koordineli LP çözülemedi (kısıtlar fazla sıkı olabilir); su bütçesini gevşetin.",
                        "The coordinated LP could not be solved (constraints may be too tight); relax the water budget."))
        coord = cur.copy()
        shadow = float("nan")

    # Koordinasyonsuz: örümcek ağı döngüsü
    p_exp = price_ref.copy()
    price_rows, area_rows, unc_eval = [], [], []
    x_unc = cur.copy()
    for k in range(COBWEB_YEARS):
        margin = Y * p_exp + F
        target = np.zeros((T, C))
        for t in range(T):
            xt, _, _ = solve(margin, False, types_subset=[t])
            target[t] = xt[t]
        x_unc = (1 - ADJUSTMENT_RATE) * x_unc + ADJUSTMENT_RATE * target
        ev = evaluate(x_unc)
        p_real = price_ref * ev["price_index"]
        price_rows.append(ev["price_index"])
        area_rows.append(x_unc.sum(axis=0))
        unc_eval.append(ev)
        p_exp = p_real
    unc_income = float(np.mean([e["income"] for e in unc_eval[COBWEB_BURN_IN:]]))
    unc_water = float(np.mean([e["water"] for e in unc_eval[COBWEB_BURN_IN:]]))

    ev_cur = evaluate(cur, prices=price_ref)
    ev_coord = evaluate(coord)
    tail = unc_eval[COBWEB_BURN_IN:]
    type_table = pd.DataFrame({
        "area_da": A,
        "income_current": ev_cur["type_income"],
        "income_uncoordinated": np.mean([e["type_income"] for e in tail], axis=0),
        "income_coordinated": ev_coord["type_income"],
        "water_current": ev_cur["type_water"],
        "water_uncoordinated": np.mean([e["type_water"] for e in tail], axis=0),
        "water_coordinated": ev_coord["type_water"],
    }, index=[ft.id for ft in types])
    metrics = pd.DataFrame({
        "current": {"income": ev_cur["income"], "water": ev_cur["water"]},
        "uncoordinated": {"income": unc_income, "water": unc_water},
        "coordinated": {"income": ev_coord["income"], "water": ev_coord["water"]},
    }).T
    metrics["overdraft"] = (metrics["water"] - budget).clip(lower=0)
    metrics["income_per_da"] = metrics["income"] / total_area
    metrics["water_per_da"] = metrics["water"] / total_area

    curve = []
    for f in np.round(np.arange(0.4, 1.21, 0.1), 2):
        x, r, d = solve(margin_ref, True, water_budget=f * water_cur)
        if r.status == 0:
            curve.append({"fraction": f, "shadow_price": d, "income": evaluate(x)["income"]})
    budget_curve = pd.DataFrame(curve)

    years_lbl = [plan_start_year + k for k in range(COBWEB_YEARS)]
    return BasinResult(
        farm_types=types, crop_ids=crop_ids, current=cur, coordinated=coord, uncoordinated_last=x_unc,
        metrics=metrics,
        price_path=pd.DataFrame(price_rows, columns=crop_ids, index=years_lbl),
        area_path=pd.DataFrame(area_rows, columns=crop_ids, index=years_lbl),
        shadow_price_water=float(shadow) if shadow is not None else float("nan"),
        water_budget_m3=budget, budget_curve=budget_curve,
        price_of_anarchy_income=ev_coord["income"] - unc_income,
        price_of_anarchy_water=unc_water - ev_coord["water"],
        currency_symbol=basin.currency_symbol, lp_status=lp_status, notes=notes, type_table=type_table,
    )


def cooperative_sharing(res: BasinResult) -> pd.DataFrame:
    """Kooperatif kazanç paylaşımı: koordineli planın getirdiği ek gelir üyelere alan payıyla dağıtılır.

    Her üye (çiftlik tipi) önce "herkes kendi başına" durumundaki gelirini garanti alır; koordinasyonla
    oluşan toplam fazlanın (koordineli − kendi başına) alan payı kadarını üstüne ekler. Koordineli planda
    su yoğun üründen vazgeçip gelir kaybeden üye, farkı kooperatiften TRANSFER olarak alır; kazanan üye öder.
    Transferlerin toplamı sıfırdır. Fazla negatifse (koordinasyon bu su bütçesinde kazandırmıyorsa)
    paylaşım kayıp paylaşımıdır ve arayüz bunu söyler.
    """
    tt = res.type_table.copy()
    a = tt["area_da"]
    surplus = float(tt["income_coordinated"].sum() - tt["income_uncoordinated"].sum())
    tt["income_after"] = tt["income_uncoordinated"] + surplus * a / a.sum()
    tt["transfer"] = tt["income_after"] - tt["income_coordinated"]
    for c in ("income_uncoordinated", "income_coordinated", "income_after", "transfer"):
        tt[c + "_per_da"] = tt[c] / a
    tt["gain_per_da"] = tt["income_after_per_da"] - tt["income_uncoordinated_per_da"]
    tt["water_saved_per_da"] = (tt["water_uncoordinated"] - tt["water_coordinated"]) / a
    tt.attrs["surplus"] = surplus
    return tt
