# Budget & Revenue Financial Modeling

A 12-month forward-looking financial model with three scenarios (Bear, Base, Bull), full P&L build, variance analysis, and break-even calculation.

---

## What It Does

1. **Builds a full monthly P&L** from revenue down to net income across three scenarios
2. **Scenario analysis** — Bear, Base, and Bull cases with different revenue growth rates and cost structures
3. **Break-even analysis** — calculates monthly break-even revenue and cushion vs actuals
4. **Variance analysis** — quantifies Bear vs Base and Bull vs Base delta on revenue and net income
5. **Exports** a summary table, charts, and a full CSV of all model outputs

---

## Model Structure

```
Revenue
  − COGS (variable, % of revenue)
= Gross Profit
  − Fixed Costs (salaries, rent, marketing, G&A — inflation-adjusted)
= EBITDA
  − Depreciation & Amortization
= EBIT
  − Interest Expense
= EBT
  − Income Tax (25.8%)
= Net Income
  + D&A (add back)
= Free Cash Flow (proxy)
```

---

## Scenarios

| Scenario | Monthly Rev Growth | COGS % of Revenue |
|---|---|---|
| Bear | 1.0% | 48% |
| Base | 2.5% | 42% |
| Bull | 4.0% | 38% |

Fixed costs grow at 0.3%/month (~3.6% annualized inflation). Starting revenue: $120,000/month.

---

## Output

| File | Description |
|---|---|
| `budget_model_charts.png` | 4-panel chart: revenue, EBITDA, P&L waterfall, gross margin |
| `budget_model_output.csv` | Full monthly model output for all scenarios |

---

## Installation & Usage

```bash
pip install pandas numpy matplotlib openpyxl
python budget_model.py
```

---

## Key Parameters (configurable at top of script)

| Parameter | Default | Description |
|---|---|---|
| `BASE_REVENUE_START` | $120,000 | January starting revenue |
| `INFLATION_MONTHLY` | 0.3% | Monthly fixed cost inflation |
| `MONTHLY_DA` | $3,333 | Straight-line D&A |
| `MONTHLY_INTEREST` | $2,917 | Interest on $500k term loan @ 7% |
| `TAX_RATE` | 25.8% | Effective income tax rate |

---

*Author: Adebola Awokoya — Applied Mathematics, Towson University (2024)*
