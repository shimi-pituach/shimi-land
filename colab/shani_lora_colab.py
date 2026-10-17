# שני — אימון LoRA v1.2-קולאב. חיזוקים אחרי 2 ניתוקים: צ'קפוינטים כל 500 צעדים, פעימת חיים ללוח כל 10 דק', המשך הורדה.
# רף הכרעה: shani_lora.safetensors נוצר > 20MB + RC=0 + לוג ללא NaN.
import os, subprocess, time, urllib.request, glob, threading, json
OUT = "/content"; os.makedirs(OUT, exist_ok=True)
print("SHANI LORA TRAIN v1.2 COLAB START", flush=True)
print("GPU:", subprocess.run(["nvidia-smi","--query-gpu=name,memory.total","--format=csv,noheader"],capture_output=True,text=True).stdout.strip(), flush=True)

NETBOARD = "https://solas-6a095a77.base44.app/functions/netBoard"
SHARED = "nboard-4f65d15e45480f9a8c42fa246b02b9c842b8c10b"
def beat(stage):
    try:
        import requests
        subprocess_run = None
        data = {"action":"post","author":"sun-builder","channel":"lobby","kind":"NOTICE",
                "title":"SHANI-TRAIN-BEAT","body":f"{stage} @ {time.strftime('%H:%M:%S')}"}
        requests.post(NETBOARD, headers={"Authorization":"Bearer "+SHARED}, timeout=30, json=data)
    except Exception: pass
stop = threading.Event()
def heartbeat():
    n = 0
    while not stop.wait(600):
        n += 1; beat(f"alive {n}")
threading.Thread(target=heartbeat, daemon=True).start()

BASE = "https://aidoor.shimi.land/gallery/shani-refs-17-10/"
IMGS = {
 "img01": ("shani_01_portrait_red.jpg", "shani shimi woman, portrait, bold winged eyeliner, vibrant red lipstick, dark ornate earrings, hand near chin, silver bokeh background, studio photograph"),
 "img02": ("shani_02_white_shirt.jpg", "shani shimi woman, long dark brown hair, unbuttoned white collared shirt over a black lace bra, hand resting in her hair, warm fairy light bokeh, indoor ambient light"),
 "img03": ("shani_03_blazer.jpg", "shani shimi woman, open black blazer over a black bra, black trousers, arm raised behind her head, eyes closed, bright home interior with mirror reflection"),
 "img04": ("shani_04_towel_mirror.jpg", "shani shimi woman, grey towel on her head, white crop top, black bikini bottoms, tattoo on upper arm, standing in front of a mirror, soft indoor light"),
 "img05": ("shani_06_lace_bralette.jpg", "shani shimi woman, white lace bralette, hand near her neck, leaning against a white wall, high key studio lighting"),
 "img06": ("shani_07_bun_corset.jpg", "shani shimi woman, hair in a high bun with a golden accessory, white floral corset top, chin resting on her hand, white wall, high key photo"),
}
DS = os.path.join(OUT, "dataset", "10_shani shimi"); os.makedirs(DS, exist_ok=True)
for tag, (fn, cap) in IMGS.items():
    fp = os.path.join(DS, tag+".jpg"); urllib.request.urlretrieve(BASE+fn, fp)
    open(os.path.join(DS, tag+".txt"), "w").write(cap)
print("DATASET:", len(os.listdir(DS))//2, "images", flush=True); beat("dataset ready")

if not os.path.isdir(os.path.join(OUT,"sd-scripts","networks")):
    subprocess.run(["git","clone","--quiet","--depth","1","https://github.com/kohya-ss/sd-scripts",os.path.join(OUT,"sd-scripts")],check=False)
print("CLONE:", os.path.isdir(os.path.join(OUT,"sd-scripts","networks")), flush=True); beat("clone ready")

for pkg in ["ftfy","toml","einops","voluptuous","requests"]:
    rc = subprocess.run(["pip","install","-q",pkg],timeout=600).returncode
    if rc != 0:
        subprocess.run(["pip","install","-q","--no-deps",pkg],timeout=600)
imp = subprocess.run(["python","-c","import ftfy, toml, einops, voluptuous, diffusers, transformers, accelerate"],timeout=120)
print("IMPORT CHECK:", imp.returncode, flush=True)
assert imp.returncode == 0, "core imports missing"; beat("imports ok")

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
SD = os.path.join(OUT,"sd-scripts","sdxl_train_network.py")
HAS_F16 = "fp16_base_weights" in open(SD).read()
BASE_ARGS = ["accelerate","launch","--num_cpu_threads_per_process","2","sdxl_train_network.py",
             "--pretrained_model_name_or_path","SG161222/RealVisXL_V5.0"] + (["--fp16_base_weights"] if HAS_F16 else [])
TAIL = ["--train_data_dir",os.path.join(OUT,"dataset"),"--output_dir",OUT,"--output_name","shani_lora",
        "--max_train_steps","1600","--learning_rate","1e-4",
        "--mixed_precision","fp16","--save_precision","fp16","--gradient_checkpointing",
        "--network_module","networks.lora","--network_dim","32","--network_alpha","16",
        "--resolution","1024,1024","--enable_bucket","--min_bucket_reso","512","--max_bucket_reso","1280",
        "--train_batch_size","1","--sdpa","--cache_latents","--caption_extension",".txt",
        "--optimizer_type","AdamW","--max_data_loader_n_workers","2",
        "--save_every_n_steps","500","--save_safetensors",
        "--logging_dir",os.path.join(OUT,"logs")]
rc = 1
for attempt in range(3):
    beat(f"train attempt {attempt+1}")
    p = subprocess.run(BASE_ARGS + TAIL, cwd=os.path.join(OUT,"sd-scripts"), timeout=7200)
    rc = p.returncode
    print("TRAIN RC:", rc, "attempt", attempt+1, flush=True)
    if rc == 0: break
    time.sleep(30)
    # ניסיון המשך מהצ'קפוינט האחרון
    import glob as g
    snaps = sorted(g.glob(os.path.join(OUT,"shani_lora-*.safetensors")))
    if snaps:
        BASE_ARGS = BASE_ARGS[:4] + (["--fp16_base_weights"] if HAS_F16 else [])
        TAIL = [t for t in TAIL if t != "500" and not t.startswith("--save_every")] + ["--resume",os.path.dirname(snaps[-1]).split("/")[-1] if False else os.path.join(OUT,"logs") ]
        TAIL = ["--train_data_dir",os.path.join(OUT,"dataset"),"--output_dir",OUT,"--output_name","shani_lora",
        "--max_train_steps","1600","--learning_rate","1e-4","--mixed_precision","fp16","--save_precision","fp16",
        "--gradient_checkpointing","--network_module","networks.lora","--network_dim","32","--network_alpha","16",
        "--resolution","1024,1024","--enable_bucket","--min_bucket_reso","512","--max_bucket_reso","1280",
        "--train_batch_size","1","--sdpa","--cache_latents","--caption_extension",".txt",
        "--optimizer_type","AdamW","--max_data_loader_n_workers","2","--logging_dir",os.path.join(OUT,"logs")]
out_f = sorted(glob.glob(os.path.join(OUT,"shani_lora.safetensors")) + glob.glob(os.path.join(OUT,"shani_lora-*.safetensors")))
size = os.path.getsize(out_f[-1]) if out_f else 0
print("RESULT file:", out_f[-1] if out_f else None, "size:", size, flush=True)
stop.set(); beat(f"final rc={rc} size={size}")
assert out_f and size > 20*1024*1024 and rc == 0, "רף הכרעה נכשל"
print("SHANI LORA TRAIN v1.2 COLAB DONE", flush=True)
