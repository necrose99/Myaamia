# algic_ety_applet_v3.py — Kilahkwaani v2 Integration Patch

## 1. Add to `<head>` (before closing `</head>`)

```html
<!-- Catrinity local font (download to static/) -->
<link rel="preload" href="/static/Catrinity.otf" as="font" type="font/otf" crossorigin/>
<link rel="preload" href="/static/CatrinityFlags.otf" as="font" type="font/otf" crossorigin/>

<!-- opentype.js (optional — only needed for subsetting) -->
<!-- <script src="https://cdn.jsdelivr.net/npm/opentype.js/dist/opentype.min.js"></script> -->

<!-- Kilahkwaani v2 — fonts + speech -->
<script src="/static/kilahkwaani_v2.js"></script>
```

## 2. Replace `annotate()` in the template's `<script>` block

Remove the existing `function annotate(text, lang) { ... }` entirely.
Kilahkwaani.init() registers its own version and patchApplet() overwrites `window.annotate`.

## 3. Add `data-*` attributes to entry cards in `renderRes()`

Change:
```js
<div class="entry-card" onclick="loadDet('${encodeURIComponent(r.form)}','${r.lang}')">
```
To:
```js
<div class="entry-card"
     data-form="${eh(r.form)}"
     data-lang="${r.lang}"
     data-ipa="${eh(r.ipa||'')}"
     onclick="loadDet('${encodeURIComponent(r.form)}','${r.lang}')">
```

## 4. Add `/static/` route to Flask app

```python
from flask import send_from_directory

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('./static', filename)
```

Create `./static/` directory and place:
- `kilahkwaani_v2.js`
- `Catrinity.otf`       (from https://catrinity-font.de/downloads/Catrinity.otf)
- `CatrinityFlags.otf`  (from https://catrinity-font.de/downloads/CatrinityFlags.otf)

## 5. Font-face unicode-range strategy

| Font            | Block                        | Languages           |
|-----------------|------------------------------|---------------------|
| BJ Cree         | U+1400–167F (UCAS)           | cre, csw (Cree)     |
| Noto Sans CA    | U+1400–167F (UCAS fallback)  | all syllabic         |
| Catrinity       | U+E480–E49F (GLAS PUA)       | pot, sac, kic legacy |
| Catrinity       | U+0250–02AF (IPA)            | all (tooltip IPA)   |
| IM Fell English | Latin                        | mia, kic, sha, mia  |

## 6. Initialise in template (end of `<body>`)

```html
<script>
  Kilahkwaani.init({
    catrinityPath:      '/static/Catrinity.otf',
    catrinityFlagsPath: '/static/CatrinityFlags.otf',
    googleFontsEnabled: true,   // loads BJ Cree + Noto Sans CA from Google
    ttsEnabled:         true,
  });
</script>
```

## 7. Per-card speak button (auto-injected by patchApplet)

After `renderRes()` populates the grid, Kilahkwaani adds:
- 🔊 **speak button** on every card using the card's `data-lang` profile
- **ᓂ toggle button** on Cree cards (switches SRO ↔ UCAS display)
- **E480 toggle button** on Potawatomi cards (switches Roman ↔ GLAS display)

## 8. Manual speak API

```js
// Speak a word (orthographic form, auto-converts to IPA internally)
Kilahkwaani.speak('nipi', 'mia', 'female');

// Speak from a corpus entry object (uses stored IPA directly)
Kilahkwaani.speakEntry({ form: 'nipi', lang: 'mia', ipa: 'niːpi' }, 'male');

// Convert Cree SRO to syllabics for display
Kilahkwaani.sroToSyllabics('nipi');   // → 'ᓂᐱ'

// Detect script of a string
Kilahkwaani.detectScript('ᓂᐱ');     // → 'ucas'
Kilahkwaani.detectScript('\uE480');  // → 'glas'
Kilahkwaani.detectScript('nipi');    // → 'roman'

// Annotate text with phoneme tooltips + TTS buttons
document.querySelector('.hw').innerHTML = Kilahkwaani.annotateText('nipi', 'mia');

// Subset Catrinity to Algic blocks only (downloads trimmed font)
// Requires opentype.js loaded first
Kilahkwaani.subsetCatrinity('/static/Catrinity.otf');
```

## 9. Kilahkwaani.py → JSON pipeline

The original `Kilahkwaani.py` generates phoneme JSON consumed by this JS.
Place the JSON output at `/static/kilahkwaani_data.json` and load it:

```js
fetch('/static/kilahkwaani_data.json')
  .then(r => r.json())
  .then(data => {
    // Extend Kilahkwaani tables with corpus-specific allophones
    Object.assign(Kilahkwaani.tables.MIA_TO_IPA, data.phonemes || {});
  });
```

## 10. GLAS / Catrinity notes

- GLAS (Great Lakes Algonquian Syllabics) is in Catrinity's PUA at E480–E49F
- Primary use: Potawatomi (Catholic mission materials, 1830s–1900s)
- Secondary: Meskwaki/Fox, early Kickapoo — not pure abjad, alphasyllabary
- `CatrinityFlags.otf` covers clan/nation symbols in PUA E000–E47F
- unicode-range on @font-face means Catrinity only downloads if GLAS chars present
