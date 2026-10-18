# -*- coding: utf-8 -*-
# הורדת הלורות של רשת שימי לתיקיית הלורות של ComfyUI המקומי
# שימוש: python shimi_lora_fetch.py [נתיב ל-ComfyUI] (ברירת מחדל: חיפוש אוטומטי)
import os, sys, urllib.request

LORAS = {
    "lea_lora.safetensors":  "https://github.com/sunraz/shimi-land/releases/download/lea-lora-v1/lea_lora.safetensors",
    "shani_lora.safetensors":"https://github.com/sunraz/shimi-land/releases/download/shani-lora-v1/shani_lora.safetensors",
}

def find_loras_dir():
    cands = []
    if len(sys.argv) > 1:
        cands.append(os.path.join(sys.argv[1], "ComfyUI", "models", "loras"))
        cands.append(os.path.join(sys.argv[1], "models", "loras"))
    cands += [os.path.join(os.getcwd(), "ComfyUI", "models", "loras"),
              os.path.join(os.getcwd(), "models", "loras")]
    for c in cands:
        if os.path.isdir(os.path.dirname(os.path.dirname(c))):
            os.makedirs(c, exist_ok=True)
            return c
    print("לא מצאתי התקנת ComfyUI. הרץ מתוך תיקיית ComfyUI או העבר נתיב כפרמטר.")
    sys.exit(1)

def main():
    d = find_loras_dir()
    print("תיקיית לורות:", d)
    for fn, url in LORAS.items():
        fp = os.path.join(d, fn)
        if os.path.exists(fp) and os.path.getsize(fp) > 200 * 1024 * 1024:
            print("קיים כבר:", fn)
            continue
        print("מוריד:", fn)
        urllib.request.urlretrieve(url, fp)
        sz = os.path.getsize(fp)
        print("נשמר:", fn, sz, "בייטים")
        assert sz > 200 * 1024 * 1024, "קובץ חשוד בגודלו — הורד מחדש"
    print("הלורות שלנו במקום.")
    print("טריגרים: lea shimi | shani shimi")

if __name__ == "__main__":
    main()
