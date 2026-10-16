# wan_run_v21.py — הרצת שחזור lana82 (0:57-1:01) דרך סשן קיים של lea_lora_colab
# נכתב ע"י שימי פיתוח. מריץ את תאי wan22_lea_colab.ipynb (2,4,6,7,8) בזה אחר זה.
# v21.2: שדרוג כפוי + אימות גרסה קשיח (diffusers דורש >=0.43.3 בכימות 4-bit).
import json, subprocess, sys, urllib.request

print('── שלב 0: שדרוג bitsandbytes + התקנת תלויות ──', flush=True)
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-U', 'bitsandbytes'], check=False)
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q',
                'diffusers', 'transformers', 'accelerate', 'safetensors',
                'sentencepiece', 'einops'], check=False)

import importlib
importlib.invalidate_caches()
import bitsandbytes
from importlib.metadata import version as pkg_version
bnb_v = pkg_version('bitsandbytes')
print('✔ bitsandbytes', bnb_v, flush=True)
if tuple(int(x) for x in bnb_v.split('.')[:2]) < (0, 43):
    raise RuntimeError(f'bitsandbytes {bnb_v} ישן מדי — השדרוג לא תפס. הריצו ידנית: pip install -U bitsandbytes')

import torch
assert torch.cuda.is_available(), 'אין GPU! הסשן הזה חייב להיות GPU.'
print('✔ GPU:', torch.cuda.get_device_name(0), flush=True)

nb = json.loads(urllib.request.urlopen(
    'https://raw.githubusercontent.com/sunraz/shimi-land/main/wan22_lea_colab.ipynb'
).read().decode())

ip = get_ipython()
for i in [2, 4, 6, 7, 8]:
    code = ''.join(nb['cells'][i]['source'])
    print(f'\n═══════ תא {i} מופעל ═══════', flush=True)
    result = ip.run_cell(code)
    if result.error_in_exec:
        print(f'✗ תא {i} נכשל: {result.error_in_exec}', flush=True)
        raise result.error_in_exec
print('\n✔✔ הרצה הושלמה — הקישור לסרטון בפלט של תא 8', flush=True)
