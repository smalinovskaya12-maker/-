"""Скачивает слайды и видео публичного поста/рилса Instagram через встраиваемую версию (embed).

Работает только с публичными аккаунтами. Логин не нужен.
Некоторые рилсы с лицензионной музыкой не отдают видео — тогда скачивается только обложка.

Пример:
    python3 tools/ig_grab.py out p DZHyvwsClDg       # пост / карусель
    python3 tools/ig_grab.py out reel DPnfr00jNZ6    # рилс

Раскадровка рилса в одну картинку (нужен ffmpeg):
    ffmpeg -i out/CODE/vid00.mp4 -vf "fps=1,scale=360:-1,tile=4x3" -frames:v 1 out/CODE/frames.jpg
"""
import json
import os
import re
import subprocess
import sys


def unescape(s):
    for _ in range(3):
        try:
            s = json.loads('"' + s + '"')
        except Exception:
            s = s.replace("\\/", "/")
    return s.replace("\\/", "/")


def filename(url):
    return url.split("?")[0].rsplit("/", 1)[-1]


def main():
    out, kind, code = sys.argv[1], sys.argv[2], sys.argv[3]
    d = os.path.join(out, code)
    os.makedirs(d, exist_ok=True)
    html = subprocess.run(
        ["curl", "-sS", f"https://www.instagram.com/{kind}/{code}/embed/captioned/"],
        capture_output=True, text=True,
    ).stdout
    with open(os.path.join(d, "embed.html"), "w") as f:
        f.write(html)

    urls = {"img": [], "vid": []}
    for key, raw in re.findall(r'(display_url|video_url)\\*"\s*:\s*\\*"(.*?)\\*"', html):
        u = unescape(raw)
        bucket = "vid" if key == "video_url" else "img"
        if filename(u) not in [filename(x) for x in urls[bucket]]:
            urls[bucket].append(u)
    if not urls["img"]:
        m = re.search(r'class="EmbeddedMediaImage"[^>]*src="([^"]+)"', html)
        if m:
            urls["img"].append(m.group(1).replace("&amp;", "&"))

    for i, u in enumerate(urls["img"]):
        subprocess.run(["curl", "-sS", "-o", os.path.join(d, f"img{i:02d}.jpg"), u])
    for i, u in enumerate(urls["vid"][:1]):
        subprocess.run(["curl", "-sS", "-o", os.path.join(d, f"vid{i:02d}.mp4"), u])
    print(code, len(urls["img"]), "картинок,", len(urls["vid"][:1]), "видео")


if __name__ == "__main__":
    main()
