from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")


def load_raw():
    """Read the two raw PSID files and return them as DataFrames."""
    individuals = pd.read_excel(
        RAW_DIR / "J366679.xlsx", sheet_name="Data", engine="calamine"
    )

    pid_names = [f"PID{i}" for i in range(1, 41)]
    pid_widths = [1, 4, 3, 4, 3, 4, 3, 4, 3, *[1] * 13, 4, 3, 4, 3, 4, 3, *[1] * 12]
    parent_ids = pd.read_fwf(
        RAW_DIR / "PID23.txt", widths=pid_widths, names=pid_names, header=None
    )
    return individuals, parent_ids
