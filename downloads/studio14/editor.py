# -*- coding: utf-8 -*-
"""ShimiStudio Local — עורך וידאו מקומי (ffmpeg). אפס ענן, אפס קרדיטים.
פעולות: info, trim, speed, concat, reels, text, watermark, audio, fade, mute, reverse, rotate, eq, gif.
כל פלט נשמר ב-output/edit/ ומוחזר כשם קובץ להצגה ב-UI."""

import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output", "edit")
os.makedirs(OUT, exist_ok=True)

def _ff(*args, timeout=1800):
    p = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + list(args),
                       capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise ValueError("ffmpeg נכשל: " + (p.stderr or "")[-300])
    return p

def _probe(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,r_frame_rate,codec_type",
                        "-of", "json", path], capture_output=True, text=True)
    return json.loads(p.stdout or "{}")

def _resolve(name):
    """מאתר קובץ לפי שם בתיקיות המוכרות (output, output/edit, שורש הסטודיו)."""
    for base in [OUT, os.path.join(HERE, "output"), os.path.dirname(_HERE := HERE)]:
        p = os.path.join(base, name)
        if os.path.isfile(p):
            return p
    raise ValueError(f"קובץ לא נמצא: {name}")

def _outname(tag, ext="mp4"):
    return f"edit_{tag}_{int(time.time())}.{ext}"

def handle(body):
    op = body.get("op", "info")
    src = body.get("src") or ""
    if op not in ("concat",) and not src:
        raise ValueError("חסר src")
    path = _resolve(src) if src else None

    if op == "info":
        return {"ok": True, "info": _probe(path), "path": path}

    if op == "trim":
        out = _outname("trim")
        a, b = body.get("start", 0), body.get("end", "")
        ss = ["-ss", str(a)] if a not in ("", None, 0) else []
        to = ["-to", str(b)] if b not in ("", None) else []
        _ff(*ss, "-i", path, *to, "-c", "copy", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "speed":
        out = _outname("speed")
        f = float(body.get("factor", 1))
        if f <= 0:
            raise ValueError("factor חייב להיות חיובי")
        has_a = _has_audio(path)
        atempo = max(min(f, 2), 0.5)
        fc = f"[0:v]setpts=PTS/{f}[v]"
        maps = ["-map", "[v]"]
        if has_a:
            fc += f";[0:a]atempo={atempo}[a]"
            maps += ["-map", "[a]"]
        _ff("-i", path, "-filter_complex", fc, *maps, os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "concat":
        files = body.get("files") or []
        if not files: raise ValueError("חסר רשימת files")
        lst = os.path.join(OUT, "concat.txt")
        with open(lst, "w") as f:
            for n in files:
                f.write("file '" + _resolve(n) + "'\n")
        out = _outname("concat")
        _ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "reels":
        out = _outname("reels")
        _ff("-i", path, "-vf",
            "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "aac", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "text":
        out = _outname("text")
        t = body.get("text", "")
        size = body.get("size", 64)
        pos = {"top": "x=(w-text_w)/2:y=40", "center": "x=(w-text_w)/2:y=(h-text_h)/2",
               "bottom": "x=(w-text_w)/2:y=h-text_h-60"}.get(body.get("position", "bottom"), "")
        _ff("-i", path, "-vf",
            f"drawtext=text='{t}':fontcolor=white:fontsize={size}:box=1:boxcolor=black@0.5:boxborderw=12:{pos}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "copy", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "watermark":
        out = _outname("wm")
        img = body.get("image")
        ip = _resolve(img) if img else None
        if ip:
            _ff("-i", path, "-i", ip, "-filter_complex",
                "overlay=W-w-30:30", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "copy",
                os.path.join(OUT, out))
        else:
            t = body.get("text", "©")
            _ff("-i", path, "-vf",
                f"drawtext=text='{t}':fontcolor=white@0.7:fontsize=42:x=w-text_w-30:y=30",
                "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "copy", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "audio":
        out = _outname("audio")
        a = _resolve(body.get("audio"))
        fade = body.get("fade", 0)
        af = f"afade=t=in:d={fade}," if fade else ""
        _ff("-i", path, "-i", a, "-filter_complex",
            f"[1:a]{af}volume=1.0[a]", "-map", "0:v", "-map", "[a]", "-shortest",
            "-c:v", "copy", "-c:a", "aac", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "fade":
        out = _outname("fade")
        dur = float(body.get("duration", 1))
        info = _probe(path)
        total = float(info.get("format", {}).get("duration", 5))
        _ff("-i", path, "-vf",
            f"fade=t=in:st=0:d={dur},fade=t=out:st={max(total-dur,0)}:d={dur}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "copy", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "mute":
        out = _outname("mute")
        _ff("-i", path, "-an", "-c:v", "copy", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "reverse":
        out = _outname("rev")
        _ff("-i", path, "-vf", "reverse", "-af", "areverse" if _has_audio(path) else "anull",
            os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "rotate":
        out = _outname("rot")
        deg = body.get("deg", 90)
        vf = {"90": "transpose=1", "180": "transpose=1,transpose=1", "270": "transpose=2"}.get(str(deg), "transpose=1")
        _ff("-i", path, "-vf", vf, "-c:a", "copy", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "eq":
        out = _outname("eq")
        br = body.get("brightness", 0); ct = body.get("contrast", 1); st = body.get("saturation", 1)
        _ff("-i", path, "-vf", f"eq=brightness={br}:contrast={ct}:saturation={st}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "copy", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    if op == "gif":
        out = _outname("gif", "gif")
        _ff("-i", path, "-vf", "fps=12,scale=480:-1", "-loop", "0", os.path.join(OUT, out))
        return {"ok": True, "file": f"edit/{out}"}

    raise ValueError(f"פעולה לא מוכרת: {op}")

def _has_audio(path):
    try:
        info = _probe(path)
        return any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    except Exception:
        return False
