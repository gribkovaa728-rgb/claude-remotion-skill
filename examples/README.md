# Examples — four videos built with this skill

Every composition here was produced by Claude Code following `remotion-motion-graphics`:
theme object, five-layer stack, spring entrances, staggered choreography, and the
mandatory render → extract frames → inspect → fix → re-render loop. The audio is
synthesized by the scripts in `scripts/` — no asset downloads.

| Composition | What it shows |
|---|---|
| `HaidrrrryPromo` | 12s profile promo — spark logo sting, word reveals, staggered cards, glow CTA |
| `FocusCatPromo` | 15.5s warm app promo — pixel-art mascot drawn in code with a 2-frame walk cycle, animated focus ring, SFX + ambient pad |
| `SelfFix` | 18.5s "watch this video fix itself" — one scene that starts deliberately bad (linear, flat, simultaneous) and upgrades live as each skill rule stamps in |
| `CodeEdit` | 20s beat-synced code edit — camera inside a syntax-glow code world, zoom punches on beats, RGB-split glitch pass, 3D code-shatter finale, original 120 BPM synthesized track |

## Run

```bash
npm install
npm run audio          # synthesize SFX + music into public/sfx/ (deterministic WAVs)
npm run studio         # open Remotion Studio and browse all four
npm run render:selffix # or render:profile / render:focuscat / render:codeedit
```

Verify like the skill demands — extract stills and look at them:

```bash
npx remotion still src/index.ts SelfFix out/check_300.png --frame 300 --overwrite
```

## Notes

- `src/theme.ts` (dark tech) and `src/focuscat/theme2.ts` (warm editorial) are the
  two palettes from `references/design-rules.md`.
- `src/focuscat/PixelCat.tsx` draws the mascot as a CSS pixel grid — swap the
  sprite strings to make your own.
- `scripts/gen-sfx.mjs` and `scripts/gen-track.mjs` write 16-bit WAVs from pure
  math (no `Math.random` at render time — everything is deterministic).
