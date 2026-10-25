import matplotlib.pyplot as plt
import pandas as pd

main = pd.read_csv("results/ige_main.csv")
by_age = pd.read_csv("results/ige_by_age.csv")

COLORS = {"Single-year": "#d6336c", "Two-year average": "#1c7ed6"}


def draw_point(ax, x, row, color):
    ax.errorbar(
        x, row["ige"],
        yerr=[[row["ige"] - row["ci_low"]], [row["ci_high"] - row["ige"]]],
        fmt="o", color=color, capsize=5, markersize=7,
    )
    ax.annotate(f"{row['ige']:.3f}", (x, row["ci_high"]),
                textcoords="offset points", xytext=(0, 6),
                ha="center", color=color, fontsize=10, fontweight="bold")


# Figure 1: overall single-year vs two-year IGE
fig, ax = plt.subplots(figsize=(7, 5))
for i, row in main.iterrows():
    key = "Single-year" if row["income_measure"].startswith("Single") else "Two-year average"
    draw_point(ax, i, row, COLORS[key])
ax.set_xticks(range(len(main)))
ax.set_xticklabels(["Single-year income\n(2022)", "Two-year average income\n(2020 and 2022)"])
ax.set_xlim(-0.6, 1.6)
ax.set_ylim(0, 0.45)
ax.set_ylabel("Estimated IGE coefficient")
ax.set_title("Intergenerational Income Elasticity", fontweight="bold")
n_common = int(main["n"].iloc[0])
ax.text(0.5, -0.2, f"Common sample: {n_common:,} children ages 25-55 in separate households.\n"
        "Points are OLS coefficients; bars are 95% CIs with HC1 robust standard errors.\n"
        "Source: PSID.", transform=ax.transAxes, ha="center", va="top", fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("results/fig1_ige_overall.png", dpi=200, bbox_inches="tight")

# Figure 2: IGE by child age group
fig, ax = plt.subplots(figsize=(8, 5))
groups = ["25-34", "35-44", "45-55"]
offset = {"Single-year": -0.06, "Two-year average": 0.06}
for label, color in COLORS.items():
    sub = by_age[by_age["income_measure"] == label].set_index("age_group").loc[groups]
    xs = [i + offset[label] for i in range(len(groups))]
    ax.plot(xs, sub["ige"], color=color, linewidth=1.5, label=label)
    for x, (_, row) in zip(xs, sub.iterrows()):
        ax.errorbar(x, row["ige"],
                    yerr=[[row["ige"] - row["ci_low"]], [row["ci_high"] - row["ige"]]],
                    fmt="o", color=color, capsize=4, markersize=6)
n_by_group = by_age.drop_duplicates("age_group").set_index("age_group")["n"]
ax.set_xticks(range(len(groups)))
ax.set_xticklabels([f"{g}\n(n={n_by_group[g]:,})" for g in groups])
ax.set_xlabel("Child age in 2023")
ax.set_ylabel("Estimated IGE coefficient")
ax.set_ylim(0.15, 0.45)
ax.set_title("IGE Estimates Across the Child Life Cycle", fontweight="bold")
ax.legend(title="Income measure", frameon=False, loc="lower center")
ax.text(0.5, -0.25, "Bars are 95% CIs with HC1 robust standard errors. Source: PSID.",
        transform=ax.transAxes, ha="center", va="top", fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("results/fig2_ige_by_age.png", dpi=200, bbox_inches="tight")
print("saved results/fig1_ige_overall.png and results/fig2_ige_by_age.png")
