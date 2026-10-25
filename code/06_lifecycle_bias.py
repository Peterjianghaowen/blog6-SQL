import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm

con = duckdb.connect("data/processed/psid.duckdb", read_only=True)

sample = con.execute("""
    SELECT *,
        CASE
            WHEN child_age_2023 BETWEEN 25 AND 34 THEN '25-34'
            WHEN child_age_2023 BETWEEN 35 AND 44 THEN '35-44'
            ELSE '45-55'
        END AS age_group
    FROM matched_children
    WHERE child_age_2023 BETWEEN 25 AND 55
      AND child_income_2022 > 0 AND parent_income_2022 > 0
      AND child_income_average > 0 AND parent_income_average > 0
""").df()

specs = {
    "Single-year": ("child_income_2022", "parent_income_2022"),
    "Two-year average": ("child_income_average", "parent_income_average"),
}

rows = []
for group in ["25-34", "35-44", "45-55"]:
    sub = sample[sample["age_group"] == group]
    for label, (child_col, parent_col) in specs.items():
        y = np.log(sub[child_col])
        x = sm.add_constant(np.log(sub[parent_col]))
        fit = sm.OLS(y, x).fit(cov_type="HC1")
        low, high = fit.conf_int().loc[parent_col]
        rows.append({
            "age_group": group, "income_measure": label, "n": int(fit.nobs),
            "ige": fit.params[parent_col], "robust_se": fit.bse[parent_col],
            "ci_low": low, "ci_high": high,
        })

results = pd.DataFrame(rows)
results.to_csv("results/ige_by_age.csv", index=False)
print(results.round(3).to_string(index=False))
