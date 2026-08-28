# KPI Dictionary

> All examples in this repository use synthetic / fabricated portfolio data.

| KPI | Formula / Definition | Business interpretation |
|---|---|---|
| Walk-ins | Total shoppers observed at an outlet | Total shopper traffic available |
| Relevant Shoppers | Shoppers matching the target profile | Indicates outlet relevance |
| Category Shopper % | Relevant Shoppers / Walk-ins | Share of outlet traffic that is commercially relevant |
| Interactions | Relevant shoppers actively engaged by the promoter | Promoter engagement volume |
| Interaction Rate | Interactions / Relevant Shoppers | Ability to engage available relevant shoppers |
| Samples | Samples / trials delivered | Trial-generation volume |
| Sampling Rate | Samples / Interactions | Movement from engagement to trial |
| Buyers | Interacted shoppers who purchase | Conversion output |
| Conversion | Buyers / Interactions | Effectiveness of promoter interaction |
| Offtake | Quantity sold from outlet | Core sales output |
| Mandays | 1 promoter × 1 outlet × 1 working day | Deployment / productivity denominator |
| Offtake / Manday | Offtake / Mandays | Productivity |
| Relevant Shoppers / Manday | Relevant Shoppers / Mandays | Relevant traffic productivity |
| Availability % | Available eligible SKU-outlet-days / eligible SKU-outlet-days | Inventory health |
| Stockout Intensity | Stockout observations / eligible SKU-outlet-days | Frequency / severity of availability failure |
| Peer Benchmark | KPI comparison against relevant outlet peer set | Separates local performance from portfolio-wide averages |
| Headroom / Opportunity | Decision-support estimate using current performance and benchmark signals | Prioritises stores with plausible upside |

## Diagnostic Framework

Low offtake is not treated as a single problem.

The engine distinguishes:

1. **Outlet relevance problem** — insufficient target shoppers.
2. **Promoter engagement problem** — relevant shoppers exist but are not being engaged.
3. **Conversion problem** — engagement is not translating into buyers.
4. **Availability problem** — demand / execution exists but inventory constrains sales.
5. **Healthy / scalable outlet** — good execution and demand with further opportunity.

## Analytical Guardrail

Peer comparisons, engagement lift and other observational relationships are used as **signals**, not causal proof. The portfolio does not claim that promoter activity alone caused a sales outcome without an experimental design.
