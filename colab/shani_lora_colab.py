# שני — אימון LoRA v1.1-колаб. בסיס: shani-lora-train v1 (קגל) + התאמות קולאב.
# דאטה: 6 רפרנסים של סאן. kohya sd-scripts, SDXL LoRA על RealVisXL V5.0, trigger: "shani shimi".
# רף הכרעה (מוכרז לפני ריצה): shani_lora.safetensors נוצר > 20MB + RC=0 + לוג ללא NaN.
import os, json, subprocess, time, urllib.request, glob
OUT = "/content"; os.makedirs(OUT, exist_ok=True)
print("SHANI LORA TRAIN v1.1 COLAB START", flush=True)
print("GPU:", subprocess.run(["nvidia-smi","--query-gpu=name,memory.total","--format=csv,noheader"],capture_output=True,text=True).stdout.strip(), flush=True)

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
print("DATASET:", len(os.listdir(DS))//2, "images", flush=True)

if not os.path.isdir(os.path.join(OUT,"sd-scripts","networks")):
    subprocess.run(["git","clone","--quiet","--depth","1","https://github.com/kohya-ss/sd-scripts",os.path.join(OUT,"sd-scripts")],check=False)
print("CLONE:", os.path.isdir(os.path.join(OUT,"sd-scripts","networks")), flush=True)

for pkg in ["ftfy","toml","einops","voluptuous"]:
    rc = subprocess.run(["pip","install","-q",pkg],timeout=600).returncode
    if rc != 0:
        subprocess.run(["pip","install","-q","--no-deps",pkg],timeout=600)
imp = subprocess.run(["python","-c","import ftfy, toml, einops, voluptuous, diffusers, transformers, accelerate"],timeout=120)
print("IMPORT CHECK:", imp.returncode, flush=True)
assert imp.returncode == 0, "core imports missing"

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
        "--logging_dir",os.path.join(OUT,"logs")]
rc = 1
for attempt in range(2):
    p = subprocess.run(BASE_ARGS + TAIL, cwd=os.path.join(OUT,"sd-scripts"), timeout=7200)
    rc = p.returncode
    print("TRAIN RC:", rc, "attempt", attempt+1, flush=True)
    if rc == 0: break
    time.sleep(20)
    BASE_ARGS = BASE_ARGS[:4] + (["--fp16_base_weights"] if HAS_F16 else [])
out_f = glob.glob(os.path.join(OUT,"shani_lora.safetensors"))
size = os.path.getsize(out_f[0]) if out_f else 0
print("RESULT file:", bool(out_f), "size:", size, flush=True)
assert out_f and size > 20*1024*1024 and rc == 0, "רף הכרעה נכשל"
print("SHANI LORA TRAIN v1.1 COLAB DONE", flush=True)
