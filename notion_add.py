#!/usr/bin/env python3
"""Добавляет текст в Notion: новой страницей внутри родительской страницы
или в конец существующей страницы.

Токен берётся из переменной окружения NOTION_TOKEN.

Примеры:
  # создать новую страницу "Заметка" внутри страницы-папки
  python3 notion_add.py page <id-или-ссылка-папки> "Заметка" < text.txt

  # дописать текст в конец существующей страницы
  echo "Новый абзац" | python3 notion_add.py append <id-или-ссылка-страницы>

  # показать страницы/папки, к которым есть доступ
  python3 notion_add.py list
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
MAX_TEXT = 2000   # лимит символов в одном rich_text
MAX_BLOCKS = 100  # лимит блоков за один запрос


def call(method, path, body=None):
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        sys.exit("Нет NOTION_TOKEN в переменных окружения.")
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"Notion API {e.code}: {e.read().decode()}")


def page_id(ref):
    """Принимает id или ссылку на страницу Notion, возвращает id."""
    # id — последние 32 hex-символа пути ссылки (до ?и #)
    m = re.search(r"([0-9a-f]{32})$", re.split(r"[?#]", ref)[0].replace("-", "").lower())
    if not m:
        sys.exit(f"Не удалось найти id страницы в: {ref}")
    return m.group(1)


def rich(text):
    return [
        {"type": "text", "text": {"content": text[i:i + MAX_TEXT]}}
        for i in range(0, len(text), MAX_TEXT)
    ] or [{"type": "text", "text": {"content": ""}}]


def to_blocks(text):
    """Простой разбор markdown: заголовки #, списки -, *, 1., остальное — абзацы."""
    blocks = []
    for para in re.split(r"\n\s*\n", text.strip()):
        for line in para.splitlines():
            line = line.rstrip()
            if not line:
                continue
            kind, content = "paragraph", line
            if m := re.match(r"^(#{1,3})\s+(.*)", line):
                kind, content = f"heading_{len(m.group(1))}", m.group(2)
            elif m := re.match(r"^[-*]\s+(.*)", line):
                kind, content = "bulleted_list_item", m.group(1)
            elif m := re.match(r"^\d+[.)]\s+(.*)", line):
                kind, content = "numbered_list_item", m.group(1)
            blocks.append({"object": "block", "type": kind, kind: {"rich_text": rich(content)}})
    return blocks


def append(pid, blocks):
    for i in range(0, len(blocks), MAX_BLOCKS):
        call("PATCH", f"/blocks/{pid}/children", {"children": blocks[i:i + MAX_BLOCKS]})


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd = args[0]

    if cmd == "list":
        res = call("POST", "/search", {"filter": {"property": "object", "value": "page"}})
        for p in res["results"]:
            title = next(
                ("".join(t["plain_text"] for t in v["title"])
                 for v in p["properties"].values() if v["type"] == "title"),
                "(без названия)",
            )
            print(f"{p['id']}  {title}  {p['url']}")
        return

    text = sys.stdin.read()
    blocks = to_blocks(text)

    if cmd == "page" and len(args) == 3:
        page = call("POST", "/pages", {
            "parent": {"page_id": page_id(args[1])},
            "properties": {"title": {"title": rich(args[2])}},
            "children": blocks[:MAX_BLOCKS],
        })
        append(page["id"], blocks[MAX_BLOCKS:])
        print(page["url"])
    elif cmd == "append" and len(args) == 2:
        append(page_id(args[1]), blocks)
        print("Добавлено блоков:", len(blocks))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
