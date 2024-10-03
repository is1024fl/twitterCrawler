import json
import random
from datetime import datetime as dt

with open("info.json", "r", encoding="utf-8") as f:
    infos = json.load(f)

infos = [info for info in infos if not any(value is None for value in info.values())]

end = dt.strptime("2024-01-11T23:59:59", "%Y-%m-%dT%H:%M:%S")

infos = list({i['content']: i for i in infos}.values())
tmp_filter_infos = [i for i in infos if i['account'] != '@warhound_yin']
filter_infos  = [i for i in tmp_filter_infos if dt.strptime(i["date"], "%Y-%m-%dT%H:%M:%S.000Z") <= end]

ppl = list(set([i['account'] for i in filter_infos]))
lucky_ppl = random.choices(ppl, k=10)

print(f'總留言數: {len(infos)}')
print(f'移除推主後的留言數: {len(tmp_filter_infos)}')
print(f'移除超時後的留言數: {len(filter_infos)}')
print('----------')
print(f'留言名單: {ppl}')
print('----------')
print(f'抽選名單與留言內容:')
for p in lucky_ppl:
    print([i for i in infos if i['account'] == p][0])