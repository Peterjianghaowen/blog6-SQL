import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm

con = duckdb.connect("data/processed/psid.duckdb", read_only=True)

# Common sample: the same children are used for both regressions,
# so the two estimates differ only in how income is measured.
sample = con.execute("""
    SELECT *
    FROM matched_children
    WHERE child_age_2023 BETWEEN 25 AND 55
      AND child_income_2022 > 0 AND parent_income_2022 > 0
      AND child_income_average > 0 AND parent_income_average > 0
""").df()


def estimate_ige(data, child_col, parent_col):
    y = np.log(data[child_col])
    x = sm.add_constant(np.log(data[parent_col]))
    return sm.OLS(y, x).fit(cov_type="HC1")


specs = {
    "Single-year (2022)": ("child_income_2022", "parent_income_2022"),
    "Two-year average (2020, 2022)": ("child_income_average", "parent_income_average"),
}

rows = []
for label, (child_col, parent_col) in specs.items():
    fit = estimate_ige(sample, child_col, parent_col)
    low, high = fit.conf_int().loc[parent_col]
    rows.append({
        "income_measure": label,
        "n": int(fit.nobs),
        "ige": fit.params[parent_col],
        "robust_se": fit.bse[parent_col],
        "ci_low": low,
        "ci_high": high,
        "r_squared": fit.rsquared,
    })

results = pd.DataFrame(rows)
results.to_csv("results/ige_main.csv", index=False)
print(results.round(3).to_string(index=False))
