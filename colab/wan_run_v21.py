# wan_run_v21.py — הרצת שחזור lana82 (0:57-1:01) דרך סשן קיים של lea_lora_colab
# נכתב ע"י שימי פיתוח. מריץ את תאי wan22_lea_colab.ipynb (2,4,6,7,8) בזה אחר זה.
import json, subprocess, sys, urllib.request

print('── שלב 0: התקנת תלויות (שקט) ──', flush=True)
subprocess.run([sys.executable, '-m', 'pip', '-q', 'install',
                'diffusers', 'transformers', 'accelerate', 'safetensors',
                'sentencepiece', 'einops', 'bitsandbytes'], check=False)

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
