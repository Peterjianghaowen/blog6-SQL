import duckdb

con = duckdb.connect("data/processed/psid.duckdb")

# One row per child. A child can have up to two matched parents (mother, father).
# GROUP BY collapses those rows; AVG() combines the parents' incomes.
# A parent only counts if living in a different household from the child,
# otherwise family income would be identical by construction.
con.execute("""
    CREATE OR REPLACE TABLE matched_children AS
    SELECT
        child_1968_id,
        child_person_number,
        MAX(child_age_2023)   AS child_age_2023,
        MAX(child_income_2022) AS child_income_2022,

        -- child: two-year average of 2020 and 2022 income
        CASE
            WHEN MAX(child_income_2020) > 0 AND MAX(child_income_2022) > 0
            THEN (MAX(child_income_2020) + MAX(child_income_2022)) / 2.0
        END AS child_income_average,

        -- parent: single-year (2022); AVG ignores NULLs, so it averages
        -- over eligible parents only
        AVG(CASE
            WHEN child_family_id_2023 > 0
             AND parent_family_id_2023 > 0
             AND child_family_id_2023 <> parent_family_id_2023
             AND parent_income_2022 > 0
            THEN parent_income_2022
        END) AS parent_income_2022,

        -- parent: two-year average of 2020 and 2022, then averaged over parents
        AVG(CASE
            WHEN child_family_id_2021 > 0 AND parent_family_id_2021 > 0
             AND child_family_id_2023 > 0 AND parent_family_id_2023 > 0
             AND child_family_id_2021 <> parent_family_id_2021
             AND child_family_id_2023 <> parent_family_id_2023
             AND parent_income_2020 > 0 AND parent_income_2022 > 0
            THEN (parent_income_2020 + parent_income_2022) / 2.0
        END) AS parent_income_average,

        COUNT(*) AS n_parents_matched
    FROM parent_child_pairs
    GROUP BY child_1968_id, child_person_number
""")

print("children:", con.execute("SELECT COUNT(*) FROM matched_children").fetchone())
print("parents matched per child:", con.execute("""
    SELECT n_parents_matched, COUNT(*) FROM matched_children
    GROUP BY n_parents_matched ORDER BY n_parents_matched
""").fetchall())
print("has parent_income_2022:", con.execute(
    "SELECT COUNT(*) FROM matched_children WHERE parent_income_2022 > 0").fetchone())
print("has parent_income_average:", con.execute(
    "SELECT COUNT(*) FROM matched_children WHERE parent_income_average > 0").fetchone())
print("regression sample (age 25-55, all incomes > 0):", con.execute("""
    SELECT COUNT(*) FROM matched_children
    WHERE child_age_2023 BETWEEN 25 AND 55
      AND child_income_2022 > 0 AND parent_income_2022 > 0
      AND child_income_average > 0 AND parent_income_average > 0
""").fetchone())
