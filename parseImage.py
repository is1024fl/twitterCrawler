import json
import requests
import shutil

from pathlib import Path
from tqdm import tqdm


with open("info.json", "r", encoding="utf-8") as f:
    infos = json.load(f)

folder_name = input("輸入資料夾名稱： ")
Path(folder_name).mkdir(exist_ok=True)

for i, img_src in enumerate(tqdm(infos), 1):
    r = requests.get(img_src, stream=True)
    if r.status_code == 200:
        with open(Path('.', folder_name, str(i) + '.jpg'), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)