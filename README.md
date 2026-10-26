# -
освітній простір

## Рилс: NVIDIA GTC, роботи-каченята

```
python3 make_reel.py ВІДЕО.mp4 -o reel.mp4
python3 make_reel.py ВІДЕО.mp4 --title "Інший заголовок" -o reel.mp4
```

Потрібен ffmpeg. Шматки монтажу задаються в `SEGMENTS` на початку `make_reel.py`,
субтитри в `subtitles_uk.srt`, шрифт Montserrat Bold у `fonts/` (ліцензія OFL).
