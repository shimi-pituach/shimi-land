# -*- coding: utf-8 -*-
"""ShimiStudio — render_one.py v1.0 (16/10): רינדר בודד בלי UI, לוורקר הלוקאלי.
קלט: JSON ב-stdin. שדות: engine, prompt, negative, seed, width, height, steps, cfg, lora_dir, lora_scale, out_dir, out_name.
פלט: שורת JSON עם נתיב הקובץ ופרטי ריצה."""
import sys, os, json, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def main():
    spec = json.loads(sys.stdin.read() or "{}")
    import engines
    out_dir = spec.get("out_dir") or os.path.join(os.path.dirname(HERE), "renders")
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    img = engines.generate_image(
        spec.get("engine") or "realvisxl_v5",
        spec.get("prompt", ""),
        negative=spec.get("negative", ""),
        seed=int(spec.get("seed", 0) or 0),
        width=int(spec.get("width", 1024)),
        height=int(spec.get("height", 1536)),
        steps=int(spec.get("steps", 32)),
        cfg=float(spec.get("cfg", 6.0)),
        lora_dir=spec.get("lora_dir"),
        lora_scale=float(spec.get("lora_scale", 0.8)),
    )
    dev, _ = engines.detect_device()
    name = spec.get("out_name") or "render_%s_%d.png" % (spec.get("seed", 0), int(time.time()))
    fp = os.path.join(out_dir, name)
    img.save(fp)
    print(json.dumps({"ok": True, "file": fp,
                      "engine": spec.get("engine") or "realvisxl_v5",
                      "device": dev, "seconds": round(time.time() - t0, 1)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        print("ERROR: render failed")
        sys.exit(1)
