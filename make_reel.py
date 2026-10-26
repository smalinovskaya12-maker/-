#!/usr/bin/env python3
"""Збирає рилс 1080x1920 з відео NVIDIA GTC (Дженсен Хуанг і роботи Pollen).

Запуск:  python3 make_reel.py ВІДЕО.mp4 [--title "Заголовок"] [-o reel.mp4]
Потрібен ffmpeg. Шрифт береться з папки fonts/, субтитри з subtitles_uk.srt.
"""
import argparse, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Шматки оригіналу (секунди), у порядку показу. bw=True -> чорно-білий.
SEGMENTS = [
    dict(start=106.0, end=129.0, bw=True),   # 1:46-2:09  «Ой, ой», сальто, сміх
    dict(start=72.5,  end=103.0, bw=True),   # 1:12-1:43  «вас усі люблять... розпродали»
    dict(start=129.0, end=230.0, bw=False),  # 2:09-3:50  суть: ШІ-фабрики, агенти, фізичний ШІ, Європа
]
DEFAULT_TITLE = "Глава NVIDIA вивів на сцену армію роботів-каченят"
FONT = "Montserrat"
FADE = 0.08  # коротке згасання звуку на стиках, щоб не клацало


def srt_time(t):
    h, m, s = t.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def read_srt(path):
    items = []
    for block in re.split(r"\n\s*\n", open(path, encoding="utf-8").read().strip()):
        lines = block.strip().splitlines()
        a, b = [srt_time(x.strip()) for x in lines[1].split("-->")]
        items.append((a, b, " ".join(lines[2:])))
    return items


def ass_time(t):
    cs = int(round(t * 100))
    return "%d:%02d:%02d.%02d" % (cs // 360000, cs // 6000 % 60, cs // 100 % 60, cs % 100)


def ass_text(s):
    return s.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height:format=duration", "-of", "json", path],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    st = j["streams"][0]
    return st["width"], st["height"], float(j["format"]["duration"])


def build_ass(title, subs, vid_h, total):
    top = (1920 - vid_h) // 2          # висота верхньої чорної смуги
    bottom = top + vid_h               # де закінчується відео
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,{FONT},74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,0,4,2,70,70,0,1
Style: Sub,{FONT},56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,0,3,8,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f"Dialogue: 1,{ass_time(0)},{ass_time(total)},Title,,0,0,0,,"
          f"{{\\pos(540,{top - 60})\\blur2}}{ass_text(title)}"]
    for a, b, txt in subs:
        ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Sub,,0,0,0,,"
                  f"{{\\pos(540,{bottom + 60})\\blur1}}{ass_text(txt)}")
    return head + "\n".join(ev) + "\n"


def remap_subs(srt, segments):
    """Переносить таймкоди субтитрів з оригіналу на змонтовану стрічку."""
    out, offset = [], 0.0
    for seg in segments:
        s, e = seg["start"], seg["end"]
        for a, b, txt in srt:
            if b > s and a < e:
                out.append((offset + max(a, s) - s, offset + min(b, e) - s, txt))
        offset += e - s
    return out, offset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--title", default=DEFAULT_TITLE)
    ap.add_argument("--srt", default=os.path.join(HERE, "subtitles_uk.srt"))
    ap.add_argument("-o", "--out", default="reel.mp4")
    args = ap.parse_args()

    w, h, dur = probe(args.video)
    vid_h = int(round(1080 * h / w / 2)) * 2
    subs, total = remap_subs(read_srt(args.srt), SEGMENTS)
    ass_path = os.path.splitext(args.out)[0] + ".ass"
    open(ass_path, "w", encoding="utf-8").write(build_ass(args.title, subs, vid_h, total))

    parts, labels, inputs = [], [], []
    for i, seg in enumerate(SEGMENTS):
        s, e = seg["start"], min(seg["end"], dur)
        bw = ",hue=s=0" if seg["bw"] else ""
        inputs += ["-ss", str(s), "-t", str(e - s), "-i", args.video]
        parts.append(f"[{i}:v]setpts=PTS-STARTPTS,fps=30{bw},"
                     f"scale=1080:{vid_h},setsar=1,"
                     f"pad=1080:1920:0:(oh-ih)/2:black[v{i}]")
        parts.append(f"[{i}:a]asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d={FADE},afade=t=out:st={e - s - FADE}:d={FADE}[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    esc = lambda p: p.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
    parts.append("".join(labels) + f"concat=n={len(SEGMENTS)}:v=1:a=1[cv][ca]")
    parts.append(f"[cv]ass='{esc(ass_path)}':fontsdir='{esc(os.path.join(HERE, 'fonts'))}'[outv]")

    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(parts),
           "-map", "[outv]", "-map", "[ca]", "-c:v", "libx264", "-preset", "medium",
           "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", args.out]
    print("Довжина рилса: %.0f с" % total)
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
