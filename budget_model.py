"""
Budget & Revenue Financial Modeling
Author: Adebola Awokoya

Builds a 12-month forward-looking budget model with three scenarios
(Bear, Base, Bull). Includes revenue forecasting, expense modeling,
variance analysis, and break-even calculation. Outputs a formatted
summary and charts.

Requirements: pip install pandas numpy matplotlib openpyxl
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings("ignore")

# ── CONFIG / ASSUMPTIONS ──────────────────────────────────────────────────────

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Base-case revenue assumptions
BASE_REVENUE_START  = 120_000   # Jan starting monthly revenue ($)
BASE_REVENUE_GROWTH = 0.025     # monthly growth rate (base)

# Scenario multipliers applied to revenue growth
SCENARIOS = {
    "Bear": {"rev_growth": 0.010, "cogs_pct": 0.48, "label_color": "#E94560"},
    "Base": {"rev_growth": 0.025, "cogs_pct": 0.42, "label_color": "#0F3460"},
    "Bull": {"rev_growth": 0.040, "cogs_pct": 0.38, "label_color": "#2ECC71"},
}

# Fixed cost structure ($/ month, grows at inflation)
FIXED_COSTS = {
    "Salaries & Benefits": 35_000,
    "Rent & Utilities":    10_000,
    "Software & Tools":     3_500,
    "Marketing":            8_000,
    "G&A / Other":          4_500,
}
INFLATION_MONTHLY = 0.003   # ~3.6% annualized

# Depreciation (straight-line on $200k asset, 5-yr life)
MONTHLY_DA = 200_000 / (5 * 12)

# Interest expense ($500k term loan @ 7%)
MONTHLY_INTEREST = 500_000 * 0.07 / 12

# Tax rate
TAX_RATE = 0.258

# ── BUILD MODEL ───────────────────────────────────────────────────────────────

def build_scenario(name: str, params: dict) -> pd.DataFrame:
    rows = []
    for i, month in enumerate(MONTHS):
        # Revenue
        revenue = BASE_REVENUE_START * (1 + params["rev_growth"]) ** i

        # Variable costs (COGS as % of revenue)
        cogs = revenue * params["cogs_pct"]

        # Fixed costs with inflation
        fixed_total = sum(v * (1 + INFLATION_MONTHLY) ** i
                          for v in FIXED_COSTS.values())

        # P&L build
        gross_profit = revenue - cogs
        gross_margin = gross_profit / revenue

        ebitda = gross_profit - fixed_total
        ebit   = ebitda - MONTHLY_DA
        ebt    = ebit - MONTHLY_INTEREST
        tax    = max(ebt * TAX_RATE, 0)   # no tax benefit modeled
        net_income = ebt - tax

        # Free cash flow proxy (add back D&A, no capex change)
        fcf = net_income + MONTHLY_DA

        rows.append({
            "Month":        month,
            "Scenario":     name,
            "Revenue":      revenue,
            "COGS":         cogs,
            "Gross Profit": gross_profit,
            "Gross Margin": gross_margin,
            "Fixed Costs":  fixed_total,
            "EBITDA":       ebitda,
            "D&A":          MONTHLY_DA,
            "EBIT":         ebit,
            "Interest":     MONTHLY_INTEREST,
            "EBT":          ebt,
            "Tax":          tax,
            "Net Income":   net_income,
            "FCF":          fcf,
        })
    return pd.DataFrame(rows)

all_scenarios = pd.concat([build_scenario(k, v) for k, v in SCENARIOS.items()])

# ── SUMMARY TABLE ─────────────────────────────────────────────────────────────

print("── Annual Budget Summary by Scenario ($) ────────────────────────────────\n")
annual = (
    all_scenarios
    .groupby("Scenario")[["Revenue","Gross Profit","EBITDA","Net Income","FCF"]]
    .sum()
    .reindex(["Bear","Base","Bull"])
)

# Add margin columns
annual["Gross Margin"]   = all_scenarios.groupby("Scenario")["Gross Profit"].sum() / annual["Revenue"]
annual["EBITDA Margin"]  = annual["EBITDA"] / annual["Revenue"]
annual["Net Margin"]     = annual["Net Income"] / annual["Revenue"]

display = annual.copy()
for col in ["Revenue","Gross Profit","EBITDA","Net Income","FCF"]:
    display[col] = display[col].map("${:,.0f}".format)
for col in ["Gross Margin","EBITDA Margin","Net Margin"]:
    display[col] = display[col].map("{:.1%}".format)

print(display.to_string())

# ── VARIANCE ANALYSIS ─────────────────────────────────────────────────────────

print("\n── Bear vs Base vs Bull — Annual Revenue Variance ─────────────────────────\n")
base_rev  = annual.loc["Base", "Revenue"] if isinstance(annual.loc["Base","Revenue"], float) else float(annual.loc["Base","Revenue"].replace("$","").replace(",",""))
# Recompute from raw annual df
ann_raw = all_scenarios.groupby("Scenario")[["Revenue","Net Income"]].sum()
for s in ["Bear","Bull"]:
    rev_var  = ann_raw.loc[s,"Revenue"]  - ann_raw.loc["Base","Revenue"]
    ni_var   = ann_raw.loc[s,"Net Income"] - ann_raw.loc["Base","Net Income"]
    print(f"  {s} vs Base  |  Revenue: {rev_var:+,.0f}  |  Net Income: {ni_var:+,.0f}")

# ── BREAK-EVEN ANALYSIS ───────────────────────────────────────────────────────

print("\n── Monthly Break-Even Analysis (Base Case) ──────────────────────────────\n")
base_df = all_scenarios[all_scenarios["Scenario"] == "Base"].copy()
cogs_pct = SCENARIOS["Base"]["cogs_pct"]
# Break-even revenue: Fixed Costs + D&A + Interest = Rev * (1 - cogs_pct)
for _, row in base_df.iterrows():
    bep = (row["Fixed Costs"] + MONTHLY_DA + MONTHLY_INTEREST) / (1 - cogs_pct)
    cushion = (row["Revenue"] - bep) / bep
    print(f"  {row['Month']}  |  BEP: ${bep:>10,.0f}  |  Actual: ${row['Revenue']:>10,.0f}  |  Cushion: {cushion:+.1%}")

# ── CHARTS ────────────────────────────────────────────────────────────────────

colors = {s: p["label_color"] for s, p in SCENARIOS.items()}
fig = plt.figure(figsize=(16, 12))
gs  = GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

# Chart 1: Revenue by scenario
ax1 = fig.add_subplot(gs[0, 0])
for s in ["Bear","Base","Bull"]:
    d = all_scenarios[all_scenarios["Scenario"] == s]
    ax1.plot(d["Month"], d["Revenue"], marker="o", markersize=4,
             label=s, color=colors[s], linewidth=2)
ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax1.set_title("Monthly Revenue by Scenario", fontweight="bold")
ax1.set_xlabel("Month"); ax1.set_ylabel("Revenue ($)")
ax1.legend(); ax1.grid(True, alpha=0.3)

# Chart 2: EBITDA by scenario
ax2 = fig.add_subplot(gs[0, 1])
for s in ["Bear","Base","Bull"]:
    d = all_scenarios[all_scenarios["Scenario"] == s]
    ax2.plot(d["Month"], d["EBITDA"], marker="o", markersize=4,
             label=s, color=colors[s], linewidth=2)
ax2.axhline(0, color="gray", linewidth=0.7, linestyle="--")
ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax2.set_title("Monthly EBITDA by Scenario", fontweight="bold")
ax2.set_xlabel("Month"); ax2.set_ylabel("EBITDA ($)")
ax2.legend(); ax2.grid(True, alpha=0.3)

# Chart 3: Waterfall — Base case annual P&L bridge
ax3 = fig.add_subplot(gs[1, 0])
base_annual = ann_raw.loc["Base"]
rev  = all_scenarios[all_scenarios["Scenario"]=="Base"]["Revenue"].sum()
cogs_  = all_scenarios[all_scenarios["Scenario"]=="Base"]["COGS"].sum()
fixed_ = all_scenarios[all_scenarios["Scenario"]=="Base"]["Fixed Costs"].sum()
da_    = MONTHLY_DA * 12
int_   = MONTHLY_INTEREST * 12
tax_   = all_scenarios[all_scenarios["Scenario"]=="Base"]["Tax"].sum()
ni_    = all_scenarios[all_scenarios["Scenario"]=="Base"]["Net Income"].sum()

labels = ["Revenue", "COGS", "Fixed Costs", "D&A", "Interest", "Tax", "Net Income"]
values = [rev, -cogs_, -fixed_, -da_, -int_, -tax_, ni_]
running = 0
bottoms = []
for i, v in enumerate(values[:-1]):
    bottoms.append(running)
    running += v
bottoms.append(0)

bar_colors = ["#2ECC71" if v >= 0 else "#E94560" for v in values]
bar_colors[-1] = "#0F3460"
ax3.bar(labels, [abs(v) for v in values], bottom=bottoms,
        color=bar_colors, edgecolor="white", linewidth=0.5)
ax3.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax3.set_title("Annual P&L Waterfall — Base Case", fontweight="bold")
ax3.set_ylabel("Amount ($)"); ax3.tick_params(axis="x", rotation=20)
ax3.grid(True, alpha=0.2, axis="y")

# Chart 4: Gross margin % by scenario
ax4 = fig.add_subplot(gs[1, 1])
for s in ["Bear","Base","Bull"]:
    d = all_scenarios[all_scenarios["Scenario"] == s]
    ax4.plot(d["Month"], d["Gross Margin"], marker="o", markersize=4,
             label=s, color=colors[s], linewidth=2)
ax4.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax4.set_title("Gross Margin % by Scenario", fontweight="bold")
ax4.set_xlabel("Month"); ax4.set_ylabel("Gross Margin")
ax4.legend(); ax4.grid(True, alpha=0.3)

fig.suptitle("12-Month Budget & Financial Model  |  Bear / Base / Bull Scenarios",
             fontsize=14, fontweight="bold", y=1.01)
plt.savefig("budget_model_charts.png", dpi=150, bbox_inches="tight")
print("\nChart saved: budget_model_charts.png")

# ── EXPORT TO CSV ─────────────────────────────────────────────────────────────

all_scenarios.to_csv("budget_model_output.csv", index=False)
print("Data exported: budget_model_output.csv")
plt.show()
