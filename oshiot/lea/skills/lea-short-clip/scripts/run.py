#!/usr/bin/env python3
# lea-short-clip — הרכבת שורט ויראלי אנכי מהבנק (hook → frame zoom → cut → motion slowmo → CTA)
import argparse, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG, TXT, HL = "#0a0a0c", "#F5F5F5", "#7fb0ff"
W, H = 1080, 1920

def run(cmd, timeout=240):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        print("FFMPEG FAIL:", r.stderr[-300:]); sys.exit(1)

def card(path, lines):
    """כרטיס מלא. lines: [(text, font, color)] — RTL תקין בלבד (raqm)."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    y = H // 2 - len(lines) * 70
    for t, f, c in lines:
        d.text((W // 2, y), t, font=ImageFont.truetype(f[0], f[1]), fill=c, anchor="mm", direction="rtl")
        y += 150
    img.save(path)

def strip(path, text, color=HL):
    """פס טקסט שקוף לרוחב."""
    img = Image.new("RGBA", (W, 240), (10, 10, 12, 215))
    d = ImageDraw.Draw(img)
    d.text((W // 2, 120), text, font=ImageFont.truetype(FB, 62), fill=color, anchor="mm", direction="rtl")
    img.save(path)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frame", required=True); p.add_argument("--motion", required=True)
    p.add_argument("--hook", required=True); p.add_argument("--strip1", default="")
    p.add_argument("--strip2", default=""); p.add_argument("--cta", required=True)
    p.add_argument("--cta2", default=""); p.add_argument("--out", required=True)
    p.add_argument("--dh", type=float, default=1.5); p.add_argument("--df", type=float, default=2.5)
    p.add_argument("--slow", type=float, default=1.25); p.add_argument("--mlen", type=float, default=7.5)
    a = p.parse_args()
    d = tempfile.mkdtemp(prefix="short_")

    card(f"{d}/c_hook.png", [(a.hook, (FB, 88), TXT)])
    card(f"{d}/c_end.png", [(a.cta, (FB, 72), TXT), (a.cta2, (FR, 56), HL),
        ("נוצר על ידי קודה — גורם לא רשמי בסטודיו שימי", (FR, 30), "#5a6278")])
    s1 = f"{d}/s1.mp4"
    run(["ffmpeg","-y","-v","error","-loop","1","-t",str(a.dh),"-i",f"{d}/c_hook.png",
         "-c:v","libx264","-preset","medium","-crf","26","-vf","format=yuv420p,fade=t=in:st=0:d=0.3","-r","25","-an",s1])

    s2 = f"{d}/s2.mp4"
    if a.strip1:
        strip(f"{d}/t1.png", a.strip1, TXT)
        fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[b];"
              f"[b]zoompan=z='min(zoom+0.0012,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=25[z];"
              f"[z][1:v]overlay=0:H-240,format=yuv420p[v]")
        cmd = ["ffmpeg","-y","-v","error","-loop","1","-t",str(a.df),"-i",a.frame,"-i",f"{d}/t1.png",
               "-filter_complex",fc,"-map","[v]","-c:v","libx264","-preset","medium","-crf","26","-r","25","-an",s2]
    else:
        fc = f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,"
        fc += f"zoompan=z='min(zoom+0.0012,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=25,format=yuv420p[v]"
        cmd = ["ffmpeg","-y","-v","error","-loop","1","-t",str(a.df),"-i",a.frame,
               "-filter_complex",fc,"-map","[v]","-c:v","libx264","-preset","medium","-crf","26","-r","25","-an",s2]
    run(cmd)

    s3 = f"{d}/s3.mp4"
    fc = (f"[0:v]setpts={a.slow}*PTS,trim=duration={a.mlen},split[bg][fg];"
          f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=22,eq=brightness=-0.18[bgc];"
          f"[fg]scale={W}:-2[f];[bgc][f]overlay=(W-w)/2:(H-h)/2-80")
    if a.strip2:
        strip(f"{d}/t2.png", a.strip2, HL)
        fc += f";[v1][1:v]overlay=0:H-260,format=yuv420p[v]"
        cmd = ["ffmpeg","-y","-v","error","-i",a.motion,"-i",f"{d}/t2.png",
               "-filter_complex",fc.replace("[bgc][f]overlay=(W-w)/2:(H-h)/2-80","[bgc][f]overlay=(W-w)/2:(H-h)/2-80[v1]"),
               "-map","[v]","-c:v","libx264","-preset","medium","-crf","26","-r","25","-an",s3]
    else:
        fc += ",format=yuv420p[v]"
        cmd = ["ffmpeg","-y","-v","error","-i",a.motion,"-filter_complex",fc,"-map","[v]",
               "-c:v","libx264","-preset","medium","-crf","26","-r","25","-an",s3]
    run(cmd)

    s4 = f"{d}/s4.mp4"
    run(["ffmpeg","-y","-v","error","-loop","1","-t","2","-i",f"{d}/c_end.png",
         "-c:v","libx264","-preset","medium","-crf","26","-vf","format=yuv420p,fade=t=out:st=1.6:d=0.4","-r","25","-an",s4])

    cf = f"{d}/c.txt"
    open(cf,"w").write("".join(f"file '{x}'\n" for x in [s1,s2,s3,s4]))
    run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",cf,"-c","copy",a.out])
    print(f"OK {a.out} — hook {a.dh}s + frame {a.df}s (cut at {a.dh+a.df:.1f}s) + motion {a.mlen}s + CTA 2s")

if __name__ == "__main__":
    main()
