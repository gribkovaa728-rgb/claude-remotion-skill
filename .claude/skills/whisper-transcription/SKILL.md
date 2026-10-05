---
name: whisper-transcription
description: Transcribe audio or video (mp4, mov, mp3, wav, m4a…) into subtitles with OpenAI Whisper — produces an .srt file and a .json file with word-level timestamps. Use this skill EVERY time the user wants subtitles, captions, a transcript, speech-to-text, karaoke/word-synced captions, or timings of spoken words, and before building any Remotion captions over footage. Defaults: Russian language, "small" model.
---

# Whisper Transcription

Turns speech in any audio/video file into:
- `<name>.srt` — subtitles by phrase, ready for Instagram / CapCut / Premiere / YouTube;
- `<name>.json` — full text, segments, and **every word with start/end timestamps**
  (needed for karaoke captions in Remotion).

## Defaults
- Language: **Russian** (`--language ru`). Change only if the user says the speech is in another language.
- Model: **small** (`--model small`) — a good balance of quality and speed on CPU.
  Use `medium` / `large-v3` only if the user asks for higher accuracy and the machine can handle it.

## Step 1 — Check requirements
```bash
ffmpeg -version | head -1          # whisper decodes audio through ffmpeg
python3 -c "import whisper" 2>/dev/null && echo "whisper ok" || pip install openai-whisper
```
If ffmpeg is missing: `apt-get install -y ffmpeg` (Linux) or `brew install ffmpeg` (macOS).

## Step 2 — Transcribe
Use the bundled script (do not rewrite it ad hoc):
```bash
python3 .claude/skills/whisper-transcription/scripts/transcribe.py <input file> \
  [--language ru] [--model small] [--out-dir <dir>]
```
Output goes next to the input file unless `--out-dir` is given: `<name>.srt` and `<name>.json`.
The first run downloads the model (~460 MB for `small`) into `~/.cache/whisper`.

## Step 3 — Check the result
- Read the `.srt` and skim it for obvious mistakes: names, brands, terms, numbers.
  Show the user the text and ask them to confirm or correct proper names.
- Fix wrong words directly in **both** files (the JSON word list and the SRT), keeping the timestamps.
- Long lines: the script already splits SRT cues at ≤ 42 characters / ≤ 3.5 s.

## JSON format
```json
{
  "language": "ru",
  "model": "small",
  "text": "Полный текст…",
  "segments": [
    { "start": 0.0, "end": 2.4, "text": "Привет всем",
      "words": [ { "word": "Привет", "start": 0.0, "end": 0.52, "probability": 0.98 } ] }
  ],
  "words": [ { "word": "Привет", "start": 0.0, "end": 0.52, "probability": 0.98 } ]
}
```
Times are in seconds.

## Using it for Remotion captions
For word-synced (karaoke) captions convert `words` to the `Caption[]` type from
`@remotion/captions`:
```ts
const captions = json.words.map((w, i) => ({
  text: (i === 0 ? "" : " ") + w.word,
  startMs: Math.round(w.start * 1000),
  endMs: Math.round(w.end * 1000),
  timestampMs: Math.round(w.start * 1000),
  confidence: w.probability,
}));
```
Then follow `.claude/skills/remotion-motion-graphics/SKILL.md` (section 17 of its
`references/motion-patterns.md`) for the visual design.

## Troubleshooting
- **Model download fails** (403 / no network to `openaipublic.azureedge.net`): the
  environment blocks the model host. Tell the user plainly; do not swap in models from
  unknown third-party packages. Options: allow that host, copy `small.pt` into
  `~/.cache/whisper/` by hand, or ask the user for an existing .srt / plain transcript.
- **Hallucinated text in silence** (repeated phrases at the end): already mitigated with
  `condition_on_previous_text=False`; if it still happens, trim silence or re-run with `--model medium`.
- **Slow on CPU**: expected — `small` runs ~1–3× real time on 4 cores. Do not switch to
  `tiny` for Russian unless the user accepts lower accuracy.
