#!/usr/bin/env python3
"""Transcribe audio/video with openai-whisper into .srt and word-level .json.

Usage: python3 transcribe.py <input> [--language ru] [--model small] [--out-dir DIR]
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

MAX_CUE_CHARS = 42
MAX_CUE_SECONDS = 3.5


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def build_cues(words):
    """Group words into short subtitle cues (by length, duration and pauses)."""
    cues, cur = [], []
    for w in words:
        if cur:
            text = " ".join(x["word"] for x in cur + [w])
            too_long = len(text) > MAX_CUE_CHARS
            too_slow = w["end"] - cur[0]["start"] > MAX_CUE_SECONDS
            pause = w["start"] - cur[-1]["end"] > 0.6
            sentence_end = cur[-1]["word"].endswith((".", "!", "?", "…"))
            if too_long or too_slow or pause or sentence_end:
                cues.append(cur)
                cur = []
        cur.append(w)
    if cur:
        cues.append(cur)
    return cues


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--language", default="ru")
    p.add_argument("--model", default="small")
    p.add_argument("--out-dir", type=Path)
    args = p.parse_args()

    if not args.input.exists():
        sys.exit(f"Input not found: {args.input}")
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is required (apt-get install ffmpeg / brew install ffmpeg)")
    try:
        import whisper
    except ImportError:
        sys.exit("openai-whisper is not installed: pip install openai-whisper")

    model = whisper.load_model(args.model)
    result = model.transcribe(
        str(args.input),
        language=args.language,
        word_timestamps=True,
        condition_on_previous_text=False,
        fp16=False,
        verbose=False,
    )

    segments, words = [], []
    for seg in result["segments"]:
        seg_words = [
            {
                "word": w["word"].strip(),
                "start": round(w["start"], 3),
                "end": round(w["end"], 3),
                "probability": round(w.get("probability", 0.0), 3),
            }
            for w in seg.get("words", [])
            if w["word"].strip()
        ]
        segments.append(
            {
                "start": round(seg["start"], 3),
                "end": round(seg["end"], 3),
                "text": seg["text"].strip(),
                "words": seg_words,
            }
        )
        words.extend(seg_words)

    out_dir = args.out_dir or args.input.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / args.input.stem

    data = {
        "language": args.language,
        "model": args.model,
        "text": result["text"].strip(),
        "segments": segments,
        "words": words,
    }
    stem.with_suffix(".json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = []
    for i, cue in enumerate(build_cues(words), 1):
        text = " ".join(w["word"] for w in cue)
        lines += [str(i), f"{srt_time(cue[0]['start'])} --> {srt_time(cue[-1]['end'])}", text, ""]
    stem.with_suffix(".srt").write_text("\n".join(lines), encoding="utf-8")

    print(f"Saved {stem.with_suffix('.srt')} and {stem.with_suffix('.json')} ({len(words)} words)")


if __name__ == "__main__":
    main()
