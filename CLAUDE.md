# CLAUDE.md — Sheet Player (如烟)

> Read this first. It is the full handoff for this project so any fresh Claude session can continue
> seamlessly. This project was built collaboratively over a long session; the chat history does NOT
> transfer, so everything needed to continue is captured here.

## What this is
An **offline, single-file** sheet-music player PWA (`index.html`). It reads **jianpu (numbered) notation
+ guitar chords** and plays them back with a **synthesized/sampled acoustic guitar**, syncing a
note+lyric highlight. Fully transcribed song: **如烟 (五月天 / 阿信词 / 石头曲 / 王一编配)**, transcribed
and verified from the 4-page guitar score.

Matches the user's other single-file vanilla-JS PWAs (no build step, no framework, no CDN, works offline).

## How to run
- It's a static single file — but audio needs a click to start (Web Audio autoplay policy).
- Dev server (for the Claude Code preview): config **"sheet-player"** in `.claude/launch.json`
  runs `python -m http.server 8127` from the repo root. Then open `http://localhost:8127`.
- **The preview panel does NOT route audio to speakers** — open `localhost:8127` in a real browser to hear it.

## Architecture
- **Three files, no build:** `index.html` (thin shell) loads `ruyan-song.js` (shared data: song + strum + chord shapes) then `player.js` (the engine as a mountable module `window.SheetPlayer`), and calls `SheetPlayer.mount(el, {hash:true})`. **No CDN, no framework.** Raw Web Audio API.
- **`player.js` is the whole engine** — audio, look-ahead scheduler, strum, render, chord popover, and the control API — wrapped in an IIFE. All its CSS is scoped under a `.sp` root class so it can be embedded inline in another app without style collisions. `SheetPlayer` API: `mount(container,{embed,hash})`, `play({section,to,bpm,chordsOnly,loop,autoplay,…})`, `stop()`, `config()`, `onState(cb)`, `unmount()`.
- The Mastery Path app (choonang-lab/Ru-Yan-Guitar) embeds this **inline** via `SheetPlayer.mount` (no iframe), sharing the same `ruyan-song.js` + `player.js`.
- NOTE: `bake.py` predates the module split — it inlines `index.html` only; to make a true standalone it must now also inline `player.js` + `ruyan-song.js` (update pending; baking is optional).
- **Data model** — `SONG.sections[]`, each: `{name, key?, chords:[[name,beats],…], strum?, mel:[[degree,octave,beats,"lyric"],…]}`.
  - Note = `[jianpu 1–7 (0=rest), octaveOffset (+up/−down), beats, "lyric"]`. Chord = `[name, beats]`.
  - Melodies are authored once as templates, then **reused via a `rely(mel, lyricString)` helper** that
    re-lyrics a template for repeated sections. `SONG.sections` is **rebuilt from templates at load**
    (see the "Expand to full song form" block right after the `SONG` literal).
- **Look-ahead audio scheduler (CRITICAL):** `play()` builds an event list (data only) then a
  `setInterval` creates oscillators only ~0.35s ahead. **Do NOT schedule all notes/oscillators upfront** —
  that froze the main thread ~1.4s AND exceeded Web Audio's live-node ceiling → total silence. This was a
  real regression that was fixed; keep the scheduler.
- **Guitar engines (two):**
  1. Default: **Karplus-Strong physical modeling** (`ksBuffer` generates a plucked-string buffer per
     pitch, cached; `ksPluck` plays it) → body-resonance peaking EQ + lowpass + convolution reverb bus (`busIn`).
  2. Optional: **real samples** (`samplePluck`, `loadSamplePack`, `SAMPLES`) — see "Sampled guitar" below.
  - `pluck()` dispatches: sampled for open notes when `GUITAR==="sample"` and samples loaded, else Karplus.
    Muted `chk` strokes always use Karplus (samples have no muted variant).
- **Strum:** `strumChord()` rakes a chord's ~6-string voicing (`guitarVoicing`) low→high (down) / high→low
  (up), staggered. Per-section pattern chosen from the `STRUM` object.

## The transcription — fully close-up-verified (pages 1–4)
23 sections, 628 notes, key **1=A** with a bridge that modulates **转1=C** then back **转1=A**.

**Section order (linear performance form, repeats expanded):**
Intro (muted) → Verse 1 → Pre-chorus 1a 她的脸 (soft) → Pre-chorus 1b 有没有…不能在 → Chorus 1 脸上撒野 →
间奏 (muted A) → 我欠了他…有没有 (E) → 星星太阳…我的指挥 → Verse 2 → Pre-chorus 2a 和眷恋 (soft) →
Pre-chorus 2b 眼泪…机会将 → Chorus 2 故事改写还 → 月亮不忙着圆缺…能听见 → 耳际眼前此生重演是我 (转C) →
Bridge 来自漆黑 (转C) → 我又是谁 (转C, soft) → Chorus 3 玫瑰 (转A) → Chorus 3b 诗篇 → Chorus 4 花瓣 →
Chorus 4b 苦痛 → Outro 双眼…无法无天 → 能听见 我不要告别 (palm-mute) → 已经如烟 (roll, let ring).

**Octaves (all read off high-res crops):** chorus `6` = F#5 (o:0, NOT high); verse opening 在床望/华丽错觉
= low (o:−1); verse 2nd half 七岁的那一年… = mid (o:0); bridge 漆黑 / 人间瞬间 = low (o:−1); 艳 / 甜美 = low (o:−1).

**Chords (all crop-verified):**
- Verse: `Bm7 D A Bm7 D A Bm7 D A #Cm Bm7` (ii–IV–I loop + #Cm).
- Pre-chorus: `D E A E #Cm #Fm Bm`.
- Chorus tail (脸上撒野…): `D E A`.
- 我欠了他 = `E`, preceded by 2 bars of **muted A** 间奏 lead-in.
- 星星太阳 / 那么一个世界: `A E #Cm #Fm`.
- Bridge: 耳际眼前 = `D E F` (转C); 来自漆黑 = `Am G`; 我又是谁 = `D E`.
- Choruses (玫瑰/诗篇/花瓣/苦痛): `A E #Cm #Fm Bm D` (花瓣 opens `E A E …`).
- Outro: `E D E` / `D` (能听见) / `Bm7 D A` (已经如烟).

## Strum patterns (`STRUM` object — all read from TAB crops)
- `muted` — intro/间奏: open A rings the first half (beats 1–2, let-ring), muted 16th `chk` second half, up-down tag at bar end.
- `ballad` — verse/chorus body: **16th-note gallop ♪♬** (down on beat, down-up on the 16ths).
- `soft` — pre-chorus lead-ins (她的脸 / 和眷恋) + bridge tail (我又是谁): gentle sparse down-up quarters, let-ring.
- `chop` — 能听见 我不要告别: palm-mute (chord on beat, muted 16ths).
- `ring` — 已经如烟: one slow arpeggiated roll per bar, let ring.

## Sampled acoustic guitar (optional, real recordings)
- Toggle in the UI: **Guitar: Synth (modeled) ⇄ Sampled acoustic**. Default synth (works with zero assets).
- **Load samples** button fetches note-named files from `samples/guitar/` (e.g. `A3.mp3`, `C4.mp3`); or
  **…or pick files** to load them manually; or they're baked in (see below). Sampler pitch-shifts the nearest sample.
- **Free pack:** https://github.com/nbrosowsky/tonejs-instruments → `samples/guitar-acoustic/*.mp3` (CC0 / VSCO2 Community).
  Put the mp3s in `samples/guitar/`. **Claude cannot fetch binary audio** — the user downloads the pack.
- **`bake.py`** base64-embeds `samples/guitar/*.mp3` into a true standalone offline file
  `sheet-player-standalone.html` (double-click, no server). Run `python bake.py`.
- STATUS: sampler + toggle + bake.py built and verified structurally; **the sampled *tone* has not yet
  been heard/tuned** (user was downloading the pack). Samples route through the body-EQ+reverb bus — may
  need EQ tuning once heard (real recordings already have body, so the +4.5dB @115Hz peak might be boomy).

## Known approximations (choices/limits, NOT errors)
- Chord-change timing can sit a beat off a syllable — melody durations were eyeballed, not quantized.
- The up-down tag at the muted intro's bar-end is rendered muted (could be open).

## How to edit
- In-app: the **"Edit song data (JSON)"** panel (edit note/octave/lyric/chord, then Reload).
- In source: the `SONG` literal + the "Expand to full song form" rebuild block below it. Melodies use the
  `[degree, octave, beats, "lyric"]` format; add sections to `SONG.sections=[…]` in the rebuild.

## Verification method (important — Claude can't hear audio)
- Verify audio by attaching an `AnalyserNode` to `master` and reading **peak amplitude** (>0 = sound produced)
  and a **sampler tick count** (main thread responsive). `play()` should return in <30ms (no upfront freeze).
- The preview screenshot tool can time out on this large page — that's a tooling limit, not a page hang;
  a quick `preview_eval` confirms the page is responsive.

## Working style that worked here
User supplies progressively higher-res **crops** of the score; Claude reads them and fixes the transcription.
Key lesson proven repeatedly: **for optical music recognition, image resolution beats re-passes** — every
octave/chord/strum error was invisible in the blurry originals and only fixed once a clear crop arrived.

## Open threads / next steps
1. User to download the free sample pack, load it, and judge/tune the sampled guitar tone by ear.
2. Optional: run `bake.py` for the standalone single-file build.
3. Optional: wire a vision API to the drop zone for true drag-and-drop auto-transcribe (currently
   Claude-in-the-loop is the "OCR").
4. Fine-tune strum feel / chord timing by ear.
