import json
import random
from datetime import datetime as dt

CHOICE_NUM = 10
DEADLINE = dt.strptime("2024-01-11T23:59:59", "%Y-%m-%dT%H:%M:%S")

with open("info.json", "r", encoding="utf-8") as f:
    infos = json.load(f)

# remove invalid info
infos = [info for info in infos if info and all(value is not None for value in info.values())]

poster = infos[0]
filter_conds = [
    lambda info: info["account"] == poster["account"],
    lambda info: dt.strptime(info["date"], "%Y-%m-%dT%H:%M:%S.000Z") > DEADLINE
]

filtered_infos = [info for info in infos[1:] if any(info for info in filter_conds)]

# random choice
ppl = list(set([info['account'] for info in filtered_infos]))
lucky_ppl = random.choices(ppl, k=CHOICE_NUM)

# show infos
print(f'總留言數: {len(infos)}')
print(f'過濾後的留言數: {len(filtered_infos)}')
print('----------')
print(f'留言名單: {ppl}')
print('----------')
print(f'抽選名單與留言內容:')
for p in lucky_ppl:
    print([info for info in filtered_infos if info['account'] == p][0])