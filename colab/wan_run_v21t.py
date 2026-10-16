# wan_run_v21t.py — גרסת טרמינל לשחזור lana82 (0:57-1:01) · Wan 2.2 I2V 4-bit
# רץ כפרוסס עצמאי ב-VM של Colab (ללא get_ipython). פלט מלא ללוג.
import json, subprocess, sys, urllib.request

print('── שלב 0: התקנת תלויות (שקט) ──', flush=True)
subprocess.run([sys.executable, '-m', 'pip', '-q', 'install',
                'diffusers', 'transformers', 'accelerate', 'safetensors',
                'sentencepiece', 'einops', 'bitsandbytes'], check=False)

import torch
assert torch.cuda.is_available(), 'אין GPU!'
print('✔ GPU:', torch.cuda.get_device_name(0), flush=True)

nb = json.loads(urllib.request.urlopen(
    'https://raw.githubusercontent.com/sunraz/shimi-land/main/wan22_lea_colab.ipynb'
).read().decode())

ns = {'__name__': '__main__'}
for i in [2, 4, 6, 8]:
    code = ''.join(nb['cells'][i]['source'])
    print(f'\n═══════ תא {i} מופעל ═══════', flush=True)
    exec(compile(code, f'cell_{i}', 'exec'), ns)
    print(f'── תא {i} הסתיים ──', flush=True)

print('\n✔✔ הרצה הושלמה — הקישור לסרטון מודפס למעלה', flush=True)
