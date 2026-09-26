#!/usr/bin/env python3
"""Download an Instagram post (incl. every carousel slide) by its link.

Usage: python3 scripts/fetch_post.py <instagram link>

Saves slides into posts/<shortcode>/ and prints the caption plus the list of
slide files, in carousel order. Works without logging in to Instagram.
If the main method (instaloader) is blocked, falls back to the public embed
page, which gives only the caption and the first slide.
"""
import html
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def shortcode_from(link):
    m = re.search(r"instagram\.com/(?:[^/]+/)?(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)", link)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{5,}", link):
        return link
    sys.exit(f"Не схоже на посилання на пост Instagram: {link}")


def ensure_instaloader():
    try:
        import instaloader  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "instaloader"], check=True)


def fetch_with_instaloader(code, out):
    import instaloader

    L = instaloader.Instaloader(
        dirname_pattern=str(out),
        filename_pattern="slide",
        download_video_thumbnails=True,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        post_metadata_txt_pattern="",
        quiet=True,
    )
    post = instaloader.Post.from_shortcode(L.context, code)
    L.download_post(post, target=code)
    return post.caption or "", post.owner_username


def fetch_with_embed(code, out):
    req = urllib.request.Request(
        f"https://www.instagram.com/p/{code}/embed/captioned/", headers={"User-Agent": "Mozilla/5.0"}
    )
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    caption = ""
    m = re.search(r'class="Caption"(.*?)<div class="CaptionComments"', page, re.S)
    if m:
        text = re.sub(r"<br\s*/?>", "\n", m.group(1))
        caption = html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
        caption = re.sub(r"^\S+\s*", "", caption, count=1)  # drop leading username
    img = re.search(r'class="EmbeddedMediaImage"[^>]*src="([^"]+)"', page)
    if img:
        data = urllib.request.urlopen(
            urllib.request.Request(html.unescape(img.group(1)), headers={"User-Agent": UA}), timeout=30
        ).read()
        (out / "slide_1.jpg").write_bytes(data)
    return caption, None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    code = shortcode_from(sys.argv[1].strip())
    out = POSTS_DIR / code
    out.mkdir(parents=True, exist_ok=True)

    method, caption, owner = "instaloader", "", None
    ensure_instaloader()
    for attempt in range(3):
        try:
            caption, owner = fetch_with_instaloader(code, out)
            break
        except Exception as e:  # rate limit / login wall / network
            err = e
            time.sleep(2 * (attempt + 1))
    else:
        print(f"[instaloader не спрацював: {err}] — беру embed (лише підпис і 1-й слайд)", file=sys.stderr)
        method = "embed (лише перший слайд)"
        caption, owner = fetch_with_embed(code, out)

    def order(p):
        n = re.search(r"_(\d+)\.", p.name)
        return (int(n.group(1)) if n else 0, p.suffix != ".jpg")

    media = sorted(
        (p for p in out.iterdir() if p.suffix in (".jpg", ".png", ".webp", ".mp4")), key=order
    )
    (out / "caption.txt").write_text(caption, encoding="utf-8")
    print(json.dumps(
        {
            "shortcode": code,
            "owner": owner,
            "method": method,
            "folder": str(out),
            "slides": [str(p) for p in media],
            "caption": caption,
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
