# BasinShift — project page (English, for the Space Apps submission form)

> Paste section by section. Items in [brackets] must be filled in by the team: they depend on the final data run or
> on facts only the team knows. Do not quote a number you have not read off the running app.

## High-level summary

Farmers choose crop rotations by habit and last year's price, while groundwater collapses and governments impose
rotation rules. BasinShift is a decision-support tool that stress-tests a farmer's 4-year rotation against 40+ years of
NASA POWER weather and NEX-GDDP-CMIP6 2040s climate, automatically finds the best rule-compliant alternatives, explains
each one, and shows on the same screen what happens to the basin's water and crop prices if everyone makes the same
choice. We showcase it in Türkiye's Konya Closed Basin, where 739 sinkholes are on record and a 2026 rule limits maize,
potato and sugar beet to two of every four years on irrigated land.

## What it does

1. **Field stress test.** Every candidate 4-year plan is replayed over each historical 4-year period (harvest years
   1982–2025, 41 periods) with an FAO-56 daily root-zone water balance (Penman-Monteith ET0) and the FAO-33 yield
   response. Results are distributions, not single numbers: average margin, bad-period income (CVaR 5%), irrigation
   water, support payments.
2. **Automatic optimisation.** All rotations (20,736 in Konya: 12 annual crops over 4 years) are screened against
   rules-as-code packs and the farmer's water, equipment, contract, buyer and forage constraints. The Pareto front is
   reduced to three cards (Profit, Aquifer, Balance), always shown next to the farmer's current plan, with a one-sentence
   summary of the difference.
3. **Explainability.** Each card answers the five questions in the NASA brief: why suggested, evidence, benefits,
   information gaps, and risks needing local review. Every number carries a confidence label, and any dataset that is
   synthetic or a fallback is flagged on screen and in the PDF.
4. **Soil health and risk calendar.** Nitrogen fixation, organic matter, erosion/bare-soil months and pest-cycle breaks;
   month-by-month frost, heat and heavy-rain risk; "what if" sliders for rainfall and temperature; a Mann-Kendall trend
   test on the climate record.
5. **Basin coordination.** A linear programme (HiGHS) over representative farm types with a sustainable water budget,
   market limits and legal rotation shares gives the **shadow price of water** and the **cost of non-coordination**
   versus a cobweb simulation in which everyone plants on last year's price.
6. **Risk & Water Scorecard.** A one-page PDF for banks, insurers and cooperatives.

## How we addressed the challenge

The brief asks for a comparison of at least three strategies including the current rotation, with reasons, evidence,
benefits, gaps and local risks, while leaving the decision to the farmer. BasinShift shows four columns, a five-heading
explanation per plan, soil-health sub-scores, forage value, a risk calendar, scenario sliders and farmer constraints,
and every page carries the note that the decision belongs to the farmer and the local agronomist.

## NASA data

| Dataset | Role | Status in our submission |
|---|---|---|
| NASA POWER (daily agroclimatology, 1981–) | Backbone of the stress test, ET0, risk calendar | [real / synthetic — read the sidebar counter] |
| SMAP L4 (SPL4SMGP) | Initial soil moisture at planting | [real / synthetic] |
| HLS (Landsat + Sentinel-2) and MODIS MOD13Q1 NDVI | Crop-history check, bare-soil months | [real / synthetic] |
| GPM IMERG | Second rainfall source | [real / synthetic] |
| GRACE / GRACE-FO mascons | Basin-scale water storage only | [real / synthetic] |
| NEX-GDDP-CMIP6 | 2040s delta-change scenarios | [real / synthetic] |
| SRTM | Slope for erosion risk | [real / synthetic] |

Datasets marked synthetic are physically consistent placeholders with the same schema; the app labels them on every
screen. Also used: ISRIC SoilGrids, FAO-56 and FAO-33 methods. Deliberately **not** used: OpenET (no coverage of
Türkiye), ECOSTRESS (not integrated), GRACE at field scale (~300 km resolution).

## Space agency partner data / tools

[None / list if any.]

## Use of AI

No AI or machine-learning model sits in the decision path: all calculations use published FAO methods and transparent
optimisation, and the explanations are generated from fixed templates filled with computed values.

AI assistance during development: an AI coding assistant (Anthropic's Claude) was used to write and review code, tests,
documentation and this page, and to search for and summarise public sources on Turkish support payments, rotation rules
and 2026 purchase prices. The team reviewed the outputs. [State who reviewed what, and adjust to match the event's AI
disclosure rules.]

## Business model

Free for farmers. Cooperatives, sugar factories (rotation compliance of contract growers), banks and crop insurers pay
an annual licence. No hardware; open NASA data. Proposed first step: a pilot with one Konya chamber of agriculture
before the 2027 season. [No organisation has been contacted yet — change this sentence if that is no longer true.]

## Limitations

- One main crop per year; perennial alfalfa is excluded from suggestions.
- Some crop prices are announced 2026 purchase prices (wheat, barley, sugar beet, sunflower); the remaining prices, all
  costs and the rotation coefficients are assumptions and are labelled as such.
- Some 2026 support amounts are derived from published coefficients, not read from the official table.
- Farm types in the basin model are representative, not registry data.
- Price volatility is not in the field stress test.
- Climate data is 0.5°; within-field differences are not modelled.
- [State which NASA clients ran live during the event and which datasets stayed synthetic.]

## References

**Methods.** Allen, Pereira, Raes & Smith (1998), FAO Irrigation and Drainage Paper 56. Doorenbos & Kassam (1979), FAO
Irrigation and Drainage Paper 33. Rockafellar & Uryasev (2000), Journal of Risk 2(3). Ezekiel (1938), QJE 52(2).
Nerlove (1958), QJE 72(2). Mann (1945), Econometrica 13; Kendall (1975); Sen (1968), JASA 63. Huangfu & Hall (2018),
Mathematical Programming Computation 10 (HiGHS).

**Data.** NASA POWER (power.larc.nasa.gov). SMAP L4 SPL4SMGP (NSIDC DAAC). HLS and MODIS MOD13Q1 (LP DAAC, AppEEARS).
GPM IMERG Final (GES DISC). GRACE / GRACE-FO JPL mascons (PO.DAAC). Thrasher et al. (2022), Scientific Data 9, 262
(NEX-GDDP-CMIP6). SRTM GL1 (NASA/USGS). SoilGrids (ISRIC).

**Konya context and rules.** AFAD sinkhole susceptibility map and press reports on sinkhole counts. Daloğlu Çetinkaya,
Uygur & Saysel (2025). Konya Provincial Directorate of Agriculture and Forestry (2024 production shares; 2026
water-restriction statements). Ministry of Agriculture and Forestry: agricultural production planning document, 2026
support unit prices, Presidential Decision no. 10394 (basin crop pattern). TMO 2026 grain purchase prices (2 June 2026).
TÜRKŞEKER 2026–27 sugar beet price (13 October 2026). Trakya Birlik and Karadenizbirlik 2026 sunflower prices.
FAO guide on scheduled drip irrigation in the Konya Closed Basin.

**Software.** Python, NumPy, pandas, SciPy (HiGHS), Streamlit, Plotly, fpdf2, Matplotlib, PyYAML, Requests, pytest;
optional xarray, netCDF4, h5netcdf, s3fs.
