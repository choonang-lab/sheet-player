#!/usr/bin/env python3
"""
Bake the acoustic-guitar samples into a single standalone HTML file.

Usage:
    1. Download the free 'guitar-acoustic' pack (see notes below) into  samples/guitar/
       so you have files like  samples/guitar/A3.mp3, samples/guitar/C4.mp3, ...
    2. Run:  python bake.py
    3. Open the result:  sheet-player-standalone.html  (double-click, works offline, no server)

Free pack: https://github.com/nbrosowsky/tonejs-instruments  ->  samples/guitar-acoustic/*.mp3
(These samples are CC0 / public domain, from the VSCO2 Community library.)
"""
import base64, glob, os, re, sys

HERE       = os.path.dirname(os.path.abspath(__file__))
SRC        = os.path.join(HERE, "index.html")
OUT        = os.path.join(HERE, "sheet-player-standalone.html")
SAMPLE_DIR = os.path.join(HERE, "samples", "guitar")
MIME       = {"mp3": "audio/mpeg", "ogg": "audio/ogg", "wav": "audio/wav"}
PREF       = {"mp3": 0, "ogg": 1, "wav": 2}   # mp3 wins when a note has several formats

def main():
    if not os.path.isdir(SAMPLE_DIR):
        sys.exit(f"No sample folder at {SAMPLE_DIR}\nDownload the free pack into it first (see the notes at the top of this file).")

    # one file per note name, preferring mp3
    chosen = {}
    for ext in MIME:
        for f in glob.glob(os.path.join(SAMPLE_DIR, f"*.{ext}")):
            name = re.sub(r"\.\w+$", "", os.path.basename(f))
            if name not in chosen or PREF[ext] < PREF[chosen[name][1]]:
                chosen[name] = (f, ext)
    if not chosen:
        sys.exit(f"No .mp3/.ogg/.wav files found in {SAMPLE_DIR}")

    entries, total = [], 0
    for name, (f, ext) in sorted(chosen.items()):
        data = open(f, "rb").read(); total += len(data)
        b64  = base64.b64encode(data).decode()
        entries.append(f'  "{name}":"data:{MIME[ext]};base64,{b64}"')

    payload = "window.EMBEDDED_SAMPLES={\n" + ",\n".join(entries) + "\n};"
    html    = open(SRC, encoding="utf-8").read()
    idx     = html.find("<script>")
    if idx == -1:
        sys.exit("Could not find a <script> tag in index.html to inject before.")
    html = html[:idx] + f"<script>{payload}</script>\n" + html[idx:]
    open(OUT, "w", encoding="utf-8").write(html)

    print(f"Baked {len(chosen)} samples ({total/1024:.0f} KB raw audio)")
    print(f"-> {OUT}  ({os.path.getsize(OUT)/1024/1024:.1f} MB, opens offline by double-click)")

if __name__ == "__main__":
    main()
