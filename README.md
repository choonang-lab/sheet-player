# Sheet Player — 如烟

An offline, single-file web app that plays a **jianpu (numbered notation) + chords** guitar score with a
synthesized or sampled acoustic guitar, syncing note + lyric highlighting. Fully transcribed song:
**如烟 (五月天)**, transcribed and verified from the 4-page guitar score.

## Run it
- **Just play:** open `index.html` in a browser (Chrome/Edge). Click ▶ Play — audio starts on click.
- **Dev/preview:** `python -m http.server 8127` in this folder, then open `http://localhost:8127`.

## Real acoustic-guitar samples (optional)
1. Download the free **guitar-acoustic** pack from
   [tonejs-instruments](https://github.com/nbrosowsky/tonejs-instruments) (`samples/guitar-acoustic/*.mp3`,
   CC0 / public domain).
2. Put the `.mp3`s in `samples/guitar/` (keep note-name filenames like `A3.mp3`).
3. Reload, click **Load sample pack**, and switch the **Guitar** selector to **Sampled acoustic**.
4. For a true standalone single file with the samples baked in: `python bake.py` → `sheet-player-standalone.html`.

## For Claude Code
See **[CLAUDE.md](CLAUDE.md)** — full project context, architecture, the transcription details, and open threads.

## Layout
```
index.html                 the app (single self-contained file)
bake.py                    embeds samples/guitar/*.mp3 into a standalone HTML
CLAUDE.md                  full handoff / project context for Claude Code
.claude/launch.json        dev-server config (port 8127)
samples/guitar/            (you add) downloaded acoustic-guitar .mp3 samples
```
