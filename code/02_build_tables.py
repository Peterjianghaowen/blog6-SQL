import duckdb
from load_data import load_raw

individuals, parent_ids = load_raw()

con = duckdb.connect("data/processed/psid.duckdb")
con.register("individuals_raw", individuals)
con.register("parent_ids_raw", parent_ids)

# Rename the raw PSID codes into readable names
con.execute("""
    CREATE OR REPLACE TABLE individual_panel AS
    SELECT
        ER30001 AS person_1968_id,
        ER30002 AS person_number,
        ER32000 AS sex,
        ER34901 AS family_id_2021,
        ER34904 AS age_2021,
        ER81775 AS family_income_2020,
        ER35101 AS family_id_2023,
        ER35104 AS age_2023,
        ER85629 AS family_income_2022
    FROM individuals_raw
""")

con.execute("""
    CREATE OR REPLACE TABLE parent_links AS
    SELECT
        PID2  AS child_1968_id,
        PID3  AS child_person_number,
        PID4  AS mother_1968_id,
        PID5  AS mother_person_number,
        PID23 AS father_1968_id,
        PID24 AS father_person_number
    FROM parent_ids_raw
""")

# Sanity checks
print(con.execute("SELECT COUNT(*) FROM individual_panel").fetchone())
print(con.execute("SELECT COUNT(*) FROM parent_links").fetchone())

# A person is identified by BOTH parts of the ID, so this should be 0
print("duplicate persons:", con.execute("""
    SELECT COUNT(*) - COUNT(DISTINCT (person_1968_id, person_number))
    FROM individual_panel
""").fetchone())

print("links with a mother:", con.execute(
    "SELECT COUNT(*) FROM parent_links WHERE mother_1968_id > 0").fetchone())
print("links with a father:", con.execute(
    "SELECT COUNT(*) FROM parent_links WHERE father_1968_id > 0").fetchone())
