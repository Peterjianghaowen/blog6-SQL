import duckdb

con = duckdb.connect("data/processed/psid.duckdb")

# Step 1: each child is joined to the mother's record, then to the father's.
# A person is identified by BOTH person_1968_id and person_number.
con.execute("""
    CREATE OR REPLACE TABLE parent_child_pairs AS

    SELECT
        c.person_1968_id       AS child_1968_id,
        c.person_number        AS child_person_number,
        'mother'               AS parent_type,
        p.person_1968_id       AS parent_1968_id,
        p.person_number        AS parent_person_number,
        c.age_2023             AS child_age_2023,
        c.family_id_2021       AS child_family_id_2021,
        c.family_id_2023       AS child_family_id_2023,
        p.family_id_2021       AS parent_family_id_2021,
        p.family_id_2023       AS parent_family_id_2023,
        c.family_income_2020   AS child_income_2020,
        c.family_income_2022   AS child_income_2022,
        p.family_income_2020   AS parent_income_2020,
        p.family_income_2022   AS parent_income_2022
    FROM parent_links AS l
    INNER JOIN individual_panel AS c
        ON  l.child_1968_id = c.person_1968_id
        AND l.child_person_number = c.person_number
    INNER JOIN individual_panel AS p
        ON  l.mother_1968_id = p.person_1968_id
        AND l.mother_person_number = p.person_number
    WHERE l.mother_1968_id > 0

    UNION ALL

    SELECT
        c.person_1968_id,
        c.person_number,
        'father',
        p.person_1968_id,
        p.person_number,
        c.age_2023,
        c.family_id_2021,
        c.family_id_2023,
        p.family_id_2021,
        p.family_id_2023,
        c.family_income_2020,
        c.family_income_2022,
        p.family_income_2020,
        p.family_income_2022
    FROM parent_links AS l
    INNER JOIN individual_panel AS c
        ON  l.child_1968_id = c.person_1968_id
        AND l.child_person_number = c.person_number
    INNER JOIN individual_panel AS p
        ON  l.father_1968_id = p.person_1968_id
        AND l.father_person_number = p.person_number
    WHERE l.father_1968_id > 0
""")

# Sanity checks
print("pairs:", con.execute("SELECT COUNT(*) FROM parent_child_pairs").fetchone())
print(con.execute("""
    SELECT parent_type, COUNT(*) AS n_pairs
    FROM parent_child_pairs GROUP BY parent_type
""").fetchall())
print("unique children:", con.execute("""
    SELECT COUNT(*) FROM (
        SELECT DISTINCT child_1968_id, child_person_number FROM parent_child_pairs)
""").fetchone())
print("duplicate child-parent_type rows:", con.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT (child_1968_id, child_person_number, parent_type))
    FROM parent_child_pairs
""").fetchone())
