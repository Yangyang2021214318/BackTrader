# -*- coding = utf-8 -*-
# @Time: 2026/9/28 16:40
# @Author: Yang Yang
# @File: check_sample_quality
# @Software: PyCharm

from datetime import datetime
from pathlib import Path
from openpyxl import load_workbook

RAW_DIR = Path(r"D:\A股日线回测\raw_data")

for year in (2015,2019,2025):
    path = sorted((RAW_DIR/str(year)).glob("*.xlsx"))[0]
    file_date = datetime.strptime(path.name[:8],"%Y%m%d").date()










