# -*- coding = utf-8 -*-
# @Time: 2026/9/28 13:09
# @Author: Yang Yang
# @File: check_duplicates
# @Software: PyCharm

from collections import defaultdict
from hashlib import sha256
from os.path import pathsep
from pathlib import Path

YEAR_DIR = Path(r"D:\A股日线回测\raw_data\2019")

def file_hash(path):
    digest = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda : file.read(1024*1024), b""):
            digest.update(chunk)

    return digest.hexdigest()

files_by_date = defaultdict(list)
for path in YEAR_DIR.glob("*.xlsx"):
    files_by_date[path.name[:8]].append(path)

duplicate_groups = {
    date: paths
    for date, paths in files_by_date.items() if len(paths) >1
}

identical = []
different = []

for date, paths in sorted(duplicate_groups.items()):
    hashed ={file_hash(path) for path in paths}
    if len(hashed) ==1:
        identical.extend(hashed)
    else:
        different.extend(hashed)

print(f"重复日期：{len(duplicate_groups)}")
print(f"内容完全相同：{len(identical)}")
print(f"内容不同：{len(different)}")














