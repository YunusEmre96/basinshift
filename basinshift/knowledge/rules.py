"""Kural paketleri motoru (rules-as-code).

Her ülke/bölgenin ekim kuralları tables/rules/*.yaml dosyalarında bir
"paket" olarak durur. Ana motor değişmez; yeni bir ülke eklemek için yeni bir
YAML yazmak yeterlidir.

Desteklenen kural tipleri:
    group_max_in_window     grup ürünleri herhangi bir N yıllık pencerede en fazla k kez
    group_no_consecutive    grup ürünleri art arda iki yıl olamaz
    allowed_crops           yalnızca listedeki ürünler (havza ürün deseni)
    crop_max_consecutive    aynı ürün en fazla k yıl üst üste (AB GAEC 7)
    water_cap               yıllık sulama üst sınırı (m³/da) — yasak değil, kısıt
    crop_min_gap_from_table aynı ürün için crops.csv'deki ara verme süresi (tavsiye)
    family_no_consecutive   aynı bitki ailesi art arda (tavsiye)

Kart mantığı (yasal kurallar): ihlal olan ilk yıl SARI, ihlal ertesi yıl da
sürerse KIRMIZI. Hesaplar hem tek plan (açıklamalı) hem de binlerce plan için
vektörel yapılır.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
import yaml

from ..config import TABLES_DIR
from .tables import Crop

GREEN, YELLOW, RED = "green", "yellow", "red"


@dataclass(frozen=True)
class RulePack:
    id: str
    kind: str
    name_tr: str
    name_en: str
    status_tr: str
    status_en: str
    applies_when: dict
    rules: tuple[dict, ...]
    penalties: dict
    supports: dict

    def name(self, lang: str) -> str:
        return self.name_tr if lang == "tr" else self.name_en

    def status(self, lang: str) -> str:
        return self.status_tr if lang == "tr" else self.status_en

    def applies(self, irrigated: bool, water_restricted: bool) -> bool:
        aw = self.applies_when or {}
        if aw.get("irrigated") and not irrigated:
            return False
        if aw.get("water_restricted") and not water_restricted:
            return False
        return True


@dataclass
class Violation:
    pack_id: str
    rule_id: str
    kind: str
    position: int          # plan içindeki yıl indeksi (0..n-1)
    year: int
    text_tr: str
    text_en: str

    def text(self, lang: str) -> str:
        return self.text_tr if lang == "tr" else self.text_en


@dataclass
class RuleCheck:
    status: str
    legal: list[Violation] = field(default_factory=list)
    advisory: list[Violation] = field(default_factory=list)
    violation_positions: list[int] = field(default_factory=list)


@lru_cache(maxsize=32)
def load_rule_pack(pack_id: str) -> RulePack:
    path = TABLES_DIR / "rules" / f"{pack_id}.yaml"
    if not path.exists():
        raise KeyError(f"Kural paketi yok: {pack_id}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return RulePack(
        id=raw["id"], kind=raw.get("kind", "legal"),
        name_tr=raw.get("name_tr", raw["id"]), name_en=raw.get("name_en", raw["id"]),
        status_tr=raw.get("status_tr", ""), status_en=raw.get("status_en", ""),
        applies_when=raw.get("applies_when") or {}, rules=tuple(raw.get("rules") or []),
        penalties=raw.get("penalties") or {}, supports=raw.get("supports") or {},
    )


def list_rule_packs() -> list[str]:
    return sorted(p.stem for p in (TABLES_DIR / "rules").glob("*.yaml"))


# ---------------------------------------------------------------------------
# Vektörel değerlendirme
# ---------------------------------------------------------------------------
def _seq_matrix(plans: np.ndarray, history: list[int]) -> np.ndarray:
    """(P, H+N) dizisi: geçmiş + plan ürün indeksleri. Geçmiş yoksa -1."""
    p = plans.shape[0]
    hist = np.array(history, dtype=int).reshape(1, -1) if history else np.zeros((1, 0), int)
    return np.concatenate([np.repeat(hist, p, axis=0), plans], axis=1)


def _rule_violations(rule: dict, seq: np.ndarray, h: int, crop_ids: list[str],
                     crops: dict[str, Crop]) -> np.ndarray:
    """Bir kural için (P, N) ihlal maskesi (yalnızca plan yılları)."""
    n_total = seq.shape[1]
    n = n_total - h
    idx = {c: i for i, c in enumerate(crop_ids)}
    rtype = rule["type"]
    out = np.zeros((seq.shape[0], n), dtype=bool)

    def member(crops_list):
        ids = np.array([idx[c] for c in crops_list if c in idx], dtype=int)
        return np.isin(seq, ids) if len(ids) else np.zeros_like(seq, dtype=bool)

    if rtype == "group_max_in_window":
        m = member(rule["crops"]).astype(int)
        w, k = int(rule["window"]), int(rule["max"])
        csum = np.concatenate([np.zeros((m.shape[0], 1), int), np.cumsum(m, axis=1)], axis=1)
        for t in range(h, n_total):
            lo = max(0, t - w + 1)
            cnt = csum[:, t + 1] - csum[:, lo]
            out[:, t - h] = (cnt > k) & (m[:, t] == 1)
    elif rtype == "group_no_consecutive":
        m = member(rule["crops"])
        for t in range(max(h, 1), n_total):
            out[:, t - h] = m[:, t] & m[:, t - 1]
    elif rtype == "allowed_crops":
        allowed = member(rule["crops"])
        out[:] = ~allowed[:, h:] & (seq[:, h:] >= 0)
    elif rtype == "crop_max_consecutive":
        k = int(rule["max"])
        run = np.ones_like(seq)
        for t in range(1, n_total):
            same = (seq[:, t] == seq[:, t - 1]) & (seq[:, t] >= 0)
            run[:, t] = np.where(same, run[:, t - 1] + 1, 1)
        out[:] = run[:, h:] > k
    elif rtype == "crop_min_gap_from_table":
        gaps = np.array([crops[c].min_gap_years for c in crop_ids])
        for t in range(h, n_total):
            g = gaps[np.clip(seq[:, t], 0, None)]
            for back in range(1, int(gaps.max()) + 1):
                if t - back < 0:
                    break
                out[:, t - h] |= (seq[:, t - back] == seq[:, t]) & (back <= g) & (seq[:, t] >= 0) \
                    & ~np.isin(seq[:, t], [idx.get("fallow", -9)])
    elif rtype == "family_no_consecutive":
        fams = set(rule.get("families", []))
        fam_idx = {f: i for i, f in enumerate(sorted({crops[c].family for c in crop_ids}))}
        fam_of = np.array([fam_idx[crops[c].family] if crops[c].family in fams else -1 for c in crop_ids])
        f = np.where(seq >= 0, fam_of[np.clip(seq, 0, None)], -1)
        for t in range(max(h, 1), n_total):
            out[:, t - h] = (f[:, t] >= 0) & (f[:, t] == f[:, t - 1])
    elif rtype == "water_cap":
        pass  # yasak değil; water_cap() ile sulama sınırı olarak uygulanır
    else:
        raise ValueError(f"Bilinmeyen kural tipi: {rtype}")
    return out


def evaluate_plans(plans: np.ndarray, history: list[int], crop_ids: list[str], crops: dict[str, Crop],
                   packs: list[RulePack], irrigated: bool, water_restricted: bool) -> dict:
    """Binlerce plan için vektörel kural değerlendirmesi.

    Dönen sözlük:
        legal_viol   (P, N) bool — yasal ihlal olan plan yılları
        advisory_cnt (P,)   int  — tavsiye kuralı ihlal sayısı
        gap_viol     (P, N) bool — ara verme ihlalleri (toprak skoru için)
        family_viol  (P, N) bool
        status       (P,)   str  — green / yellow / red
    """
    seq = _seq_matrix(plans, history)
    h = len(history)
    p, n = plans.shape
    legal = np.zeros((p, n), bool)
    gap = np.zeros((p, n), bool)
    fam = np.zeros((p, n), bool)
    for pack in packs:
        if not pack.applies(irrigated, water_restricted) and pack.kind == "legal":
            continue
        for rule in pack.rules:
            v = _rule_violations(rule, seq, h, crop_ids, crops)
            if pack.kind == "legal":
                legal |= v
            elif rule["type"] == "crop_min_gap_from_table":
                gap |= v
            elif rule["type"] == "family_no_consecutive":
                fam |= v
    consecutive = (legal[:, 1:] & legal[:, :-1]).any(axis=1) if n > 1 else np.zeros(p, bool)
    status = np.where(consecutive, RED, np.where(legal.any(axis=1), YELLOW, GREEN))
    return {
        "legal_viol": legal, "gap_viol": gap, "family_viol": fam,
        "advisory_cnt": gap.sum(axis=1) + fam.sum(axis=1), "status": status,
    }


def check_plan(plan: list[str], plan_years: list[int], history: list[str], crop_ids: list[str],
               crops: dict[str, Crop], packs: list[RulePack], irrigated: bool,
               water_restricted: bool) -> RuleCheck:
    """Tek plan için açıklamalı kural kontrolü (arayüz ve 'Neden' paneli için)."""
    idx = {c: i for i, c in enumerate(crop_ids)}
    plan_arr = np.array([[idx[c] for c in plan]])
    hist = [idx[c] for c in history if c in idx]
    seq = _seq_matrix(plan_arr, hist)
    h = len(hist)
    res = RuleCheck(status=GREEN)
    legal_pos = np.zeros(len(plan), bool)
    for pack in packs:
        if pack.kind == "legal" and not pack.applies(irrigated, water_restricted):
            continue
        for rule in pack.rules:
            if rule["type"] == "water_cap":
                continue
            v = _rule_violations(rule, seq, h, crop_ids, crops)[0]
            for pos in np.flatnonzero(v):
                crop = crops[plan[pos]]
                txt_tr = f"{plan_years[pos]} · {crop.name_tr}: {rule.get('text_tr', rule['id'])}"
                txt_en = f"{plan_years[pos]} · {crop.name_en}: {rule.get('text_en', rule['id'])}"
                viol = Violation(pack.id, rule["id"], pack.kind, int(pos), plan_years[pos], txt_tr, txt_en)
                (res.legal if pack.kind == "legal" else res.advisory).append(viol)
                if pack.kind == "legal":
                    legal_pos[pos] = True
    res.violation_positions = [int(i) for i in np.flatnonzero(legal_pos)]
    if (legal_pos[1:] & legal_pos[:-1]).any():
        res.status = RED
    elif legal_pos.any():
        res.status = YELLOW
    return res


def water_cap(packs: list[RulePack], irrigated: bool, water_restricted: bool) -> float | None:
    caps = [
        float(r["m3_per_da_per_year"])
        for pk in packs if pk.applies(irrigated, water_restricted)
        for r in pk.rules if r["type"] == "water_cap"
    ]
    return min(caps) if caps else None


def support_matrix(plans: np.ndarray, legal_viol: np.ndarray, crop_ids: list[str], packs: list[RulePack],
                   irrigated: bool, water_restricted: bool) -> np.ndarray:
    """(P, N) yıllık destek tutarı (para/da), ceza mantığı uygulanmış."""
    base = np.zeros(len(crop_ids))
    bonus = np.zeros(len(crop_ids))
    yellow_loses, red_loses = False, False
    for pk in packs:
        sup = pk.supports or {}
        for c, v in (sup.get("base_per_da") or {}).items():
            if c in crop_ids:
                base[crop_ids.index(c)] = float(v)
        for c in sup.get("no_support", []) or []:
            if c in crop_ids:
                base[crop_ids.index(c)] = 0.0
        b = float(sup.get("water_restriction_bonus_per_da", 0) or 0)
        if b and water_restricted and (irrigated or not sup.get("water_restriction_bonus_irrigated_only", True)):
            for c in sup.get("water_restriction_bonus_crops", []) or []:
                if c in crop_ids:
                    bonus[crop_ids.index(c)] = b
        if pk.applies(irrigated, water_restricted):
            yellow_loses |= bool(pk.penalties.get("yellow_loses_support_that_year"))
            red_loses |= bool(pk.penalties.get("red_loses_all_support_from_then"))
    sup = base[plans] + bonus[plans]
    if yellow_loses:
        sup = np.where(legal_viol, 0.0, sup)
    if red_loses and plans.shape[1] > 1:
        red_from = np.zeros_like(legal_viol)
        red_from[:, 1:] = legal_viol[:, 1:] & legal_viol[:, :-1]
        red_from = np.maximum.accumulate(red_from, axis=1)
        sup = np.where(red_from, 0.0, sup)
    return sup
