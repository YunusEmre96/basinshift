# BasinShift — project page draft (English)

> Draft for the Space Apps submission form. Replace bracketed items, and
> re-run results with real NASA data before quoting numbers.

## High-level summary

Farmers choose crop rotations by habit and last year's price, while groundwater
collapses and governments impose rotation rules. BasinShift is a decision-support
tool that stress-tests a farmer's 4-year rotation against 40+ years of NASA POWER
weather and NEX-GDDP-CMIP6 2040s climate, finds the best rule-compliant
alternatives automatically, and shows — on the same screen — what happens to the
basin's water and crop prices if everyone makes the same choice. It runs anywhere
NASA data exists; we showcase it in Türkiye's Konya Closed Basin, where 739
sinkholes have formed and a 2026 rule limits maize, potato and sugar beet to 2 of
every 4 years.

## What it does

1. **Field stress test.** Every candidate 4-year plan is replayed over each
   historical 4-year period (1982–2025) using FAO-56 daily soil-water balance
   (Penman-Monteith ET0 from NASA POWER, initial moisture from SMAP) and FAO-33
   yield response. Results are distributions, not single numbers: average margin,
   bad-period income (CVaR 5%), irrigation water, support payments.
2. **Automatic optimisation.** All rotations (28,561 in Konya) are screened against
   rules-as-code packs and the farmer's water, equipment, contract, buyer and
   forage constraints; the Pareto front is reduced to three cards — Profit,
   Aquifer, Balance — always shown next to the farmer's current plan.
3. **Explainability.** Each card answers NASA's five questions: why suggested,
   evidence, benefits, information gaps, and risks needing local review. Every
   number carries a confidence label; synthetic or fallback data is flagged.
4. **Soil health and risk calendar.** Nitrogen fixation, organic matter,
   erosion/bare-soil months (HLS/MODIS NDVI), pest-cycle breaks; month-by-month
   frost, heat and heavy-rain risk; "what if" sliders for rainfall and temperature.
5. **Basin coordination.** A linear programme (HiGHS) over representative farm
   types with a sustainable water budget, market limits and legal rotation shares
   yields the **shadow price of water** and the **cost of non-coordination** versus
   a cobweb simulation where everyone plants on last year's price. GRACE-FO is used
   only at basin scale.
6. **Risk & Water Scorecard.** A one-page PDF for banks, insurers and cooperatives.

## NASA data used

NASA POWER (daily agroclimatology), SMAP L4 (SPL4SMGP), HLS (Landsat + Sentinel-2),
MODIS MOD13Q1, GPM IMERG, GRACE/GRACE-FO mascons, NEX-GDDP-CMIP6, SRTM.
Also: FAO-56/FAO-33 methods, ISRIC SoilGrids. Deliberately **not** used: OpenET
(no coverage of Türkiye), GRACE at field scale (~300 km resolution).

## Space agency partner data / tools

[If any.]

## Use of AI

No black-box model sits in the decision path: calculations use published FAO
methods and transparent optimisation, and explanations are template-generated
from computed values. [Describe any AI assistance used in development, per the
Space Apps rules.]

## Business model

Free for farmers. Cooperatives, sugar factories (contract growers' rotation
compliance), banks and crop insurers pay an annual licence. Zero hardware;
open NASA data. Pilot: one Konya chamber of agriculture before the 2027 season;
then the 52 water-restricted districts in Türkiye; then other basins via new rule
packs.

## Limitations (honest)

One main crop per year; prices and rotation coefficients are 2026 literature-based
assumptions; farm types in the basin model are representative; NASA API clients
other than POWER were written to documentation but not tested live during
development.

## References

[List every dataset, library and source — see docs/METHODS.md and README.]
