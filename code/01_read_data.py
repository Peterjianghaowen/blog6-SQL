from pathlib import Path
import pandas as pd

raw_dir = Path("data/raw")

# 1. 个人和家庭数据（Excel）
individuals = pd.read_excel(
    raw_dir / "J366679.xlsx", sheet_name="Data", engine="calamine"
)
print("individuals:", individuals.shape)
print(individuals.head())

# 2. Parent Identification File（定宽 txt，没有表头）
pid_names = [f"PID{i}" for i in range(1, 41)]
pid_widths = [1, 4, 3, 4, 3, 4, 3, 4, 3, *[1] * 13, 4, 3, 4, 3, 4, 3, *[1] * 12]
assert len(pid_widths) == 40

parent_ids = pd.read_fwf(
    raw_dir / "PID23.txt", widths=pid_widths, names=pid_names, header=None
)
print("parent_ids:", parent_ids.shape)
print(parent_ids[["PID2", "PID3", "PID4", "PID5", "PID23", "PID24"]].head())
