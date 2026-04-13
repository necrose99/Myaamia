/**
 * kilahkwaani_v2.js
 * =================
 * Font loading, GLAS/UCAS script rendering, and speech synthesis
 * for the Algic Etymology Applet (algic_ety_applet_v3.py).
 *
 * Covers:
 *   - Cree syllabics (UCAS U+1400–167F) via BJ Cree / Noto Sans CA
 *   - GLAS (Great Lakes Algonquian Syllabics, PUA E480–E49F) via Catrinity
 *   - Potawatomi GLAS script rendering with tooltip transliteration
 *   - Miami-Illinois (Myaamia) speech synthesis — IPA-based, Italian voice
 *     approximation per original Kilahkwaani.js approach
 *   - Kickapoo Roman speech synthesis
 *   - Cree SRO → syllabics display toggle
 *   - opentype.js font subsetting utility (trim Catrinity to Algic blocks)
 *
 * Dependencies (CDN or local):
 *   opentype.js  — https://cdn.jsdelivr.net/npm/opentype.js/dist/opentype.min.js
 *   Web Speech API (built-in, no install)
 *
 * Font files needed (place alongside or adjust paths):
 *   Catrinity.otf     — https://catrinity-font.de/downloads/Catrinity.otf
 *   CatrinityFlags.otf — https://catrinity-font.de/downloads/CatrinityFlags.otf
 *   (BJ Cree loads from Google Fonts — requires network)
 *
 * Usage in algic_ety_applet_v3.py HTML template:
 *   <script src="/static/kilahkwaani_v2.js"></script>
 *   <script>Kilahkwaani.init({ catrinityPath: '/static/Catrinity.otf' });</script>
 *
 * Or inline the entire file between <script>…</script> tags.
 */

'use strict';

// ═══════════════════════════════════════════════════════════════════════════
// MODULE: Kilahkwaani
// ═══════════════════════════════════════════════════════════════════════════
const Kilahkwaani = (() => {

  // ── Configuration ──────────────────────────────────────────────────────────
  const CONFIG = {
    catrinityPath:      '/static/Catrinity.otf',
    catrinityFlagsPath: '/static/CatrinityFlags.otf',
    googleFontsEnabled: true,
    defaultVoiceLang:   'it-IT',   // Italian approximates Myaamia vowels best
    ttsEnabled:         true,
    subsettingEnabled:  false,      // true only if opentype.js available + CORS ok
  };

  // ── Speech profiles (mirrors original Kilahkwaani.js structure) ────────────
  const PROFILES = {
    mia: {
      male:    { lang: 'it-IT', pitch: 0.80, rate: 0.82, voiceHint: 'Giorgio'  },
      female:  { lang: 'it-IT', pitch: 1.10, rate: 0.80, voiceHint: 'Alice'    },
      neutral: { lang: 'it-IT', pitch: 0.95, rate: 0.82, voiceHint: null       },
    },
    kic: {
      // Kickapoo: slightly more clipped than Miami-Illinois
      male:    { lang: 'it-IT', pitch: 0.78, rate: 0.85, voiceHint: null },
      female:  { lang: 'it-IT', pitch: 1.08, rate: 0.83, voiceHint: null },
      neutral: { lang: 'it-IT', pitch: 0.93, rate: 0.85, voiceHint: null },
    },
    pot: {
      // Potawatomi: similar to Miami-Illinois
      male:    { lang: 'it-IT', pitch: 0.80, rate: 0.83, voiceHint: null },
      female:  { lang: 'it-IT', pitch: 1.10, rate: 0.81, voiceHint: null },
      neutral: { lang: 'it-IT', pitch: 0.95, rate: 0.83, voiceHint: null },
    },
    sac: {
      male:    { lang: 'it-IT', pitch: 0.80, rate: 0.84, voiceHint: null },
      female:  { lang: 'it-IT', pitch: 1.08, rate: 0.82, voiceHint: null },
      neutral: { lang: 'it-IT', pitch: 0.94, rate: 0.84, voiceHint: null },
    },
    cre: {
      // Cree: use a more open vowel profile; syllabics need SRO conversion first
      male:    { lang: 'it-IT', pitch: 0.77, rate: 0.80, voiceHint: null },
      female:  { lang: 'it-IT', pitch: 1.05, rate: 0.78, voiceHint: null },
      neutral: { lang: 'it-IT', pitch: 0.90, rate: 0.80, voiceHint: null },
    },
    sha: {
      male:    { lang: 'it-IT', pitch: 0.82, rate: 0.83, voiceHint: null },
      female:  { lang: 'it-IT', pitch: 1.10, rate: 0.81, voiceHint: null },
      neutral: { lang: 'it-IT', pitch: 0.96, rate: 0.83, voiceHint: null },
    },
  };

  // ── Miami-Illinois (Myaamia) phoneme → IPA → Italian-approx ───────────────
  // [ipa] → synthesis: IPA stored in DB, used for TTS; normal spellings untouched
  // Phoneme ordering: digraphs/clusters FIRST (longest-match tokenizer)
  const MIA_TO_IPA = {
    // Long vowels (digraphs first)
    'aa': 'aː',  'ii': 'iː',  'oo': 'oː',  'ee': 'eː',
    // Consonant clusters (digraphs first)
    'hk': 'hk',  'hw': 'ʍ',   'nk': 'ŋk',  'nc': 'ntʃ',
    'šk': 'ʃk',
    // Special consonants
    'š':  'ʃ',   'č':  'tʃ',  'ð':  'ð',   'θ':  'θ',
    'ʔ':  'ʔ',
    // Short vowels
    'a':  'a',   'i':  'i',   'o':  'o',   'e':  'e',
    // Regular consonants
    'k':  'k',   'p':  'p',   't':  't',   's':  's',
    'm':  'm',   'n':  'n',   'w':  'w',   'y':  'j',
    'l':  'l',   'h':  'h',
  };

  // IPA → Italian-approximation string for Web Speech API
  // The Speech Synthesis API doesn't accept IPA directly on most browsers;
  // we convert to an Italian-phoneme string that produces similar acoustics.
  const IPA_TO_IT = {
    'aː': 'a',   'iː': 'i',   'oː': 'o',   'eː': 'e',
    'a':  'a',   'i':  'i',   'o':  'o',   'e':  'e',
    'ʃ':  'sci', 'tʃ': 'ci',  'ð':  'z',   'θ':  'z',
    'ʔ':  "'",   'ŋk': 'nc',  'ntʃ':'nci', 'ʍ':  'u',
    'hk': 'ch',  'ʃk': 'sch',
    'k':  'c',   'p':  'p',   't':  't',   's':  's',
    'm':  'm',   'n':  'n',   'w':  'u',   'j':  'i',
    'l':  'l',   'h':  '',    'ʔ':  "'",
  };

  // ── Kickapoo phoneme → IPA (Voorhis/SIL) ──────────────────────────────────
  const KIC_TO_IPA = {
    'ck': 'kː',  'pp': 'pː',  'tt': 'tː',  'ss': 'sː',
    'šš': 'ʃː',  'cc': 'tʃː', 'hw': 'ʍ',   'nk': 'ŋk',
    'â':  'aː',  'ê':  'eː',  'î':  'iː',  'ô':  'oː',
    'š':  'ʃ',   'θ':  'θ',   'ʔ':  'ʔ',   'c':  'tʃ',
    'a':  'a',   'e':  'e',   'i':  'i',   'o':  'o',
    'k':  'k',   'p':  'p',   't':  't',   's':  's',
    'm':  'm',   'n':  'n',   'w':  'w',   'y':  'j',
    'h':  'h',
  };

  // ── Cree SRO (Standard Roman Orthography) ─────────────────────────────────
  // SRO → IPA for speech synthesis fallback when syllabics shown visually
  const CREE_SRO_TO_IPA = {
    'ê': 'eː', 'î': 'iː', 'ô': 'oː', 'â': 'aː',
    'e': 'e',  'i': 'i',  'o': 'o',  'a': 'a',
    'p': 'p',  't': 't',  'k': 'k',  'c': 'tʃ',
    'm': 'm',  'n': 'n',  's': 's',  'y': 'j',
    'w': 'w',  'h': 'h',
    'th': 'θ',  // th-Cree dialect
  };

  // ── UCAS (Cree syllabics) → SRO romanization ──────────────────────────────
  // Full map — same data as tooltip tables but here for TTS conversion
  const UCAS_TO_SRO = {
    'ᐁ':'ê','ᐃ':'i','ᐄ':'î','ᐅ':'o','ᐆ':'ô','ᐊ':'a','ᐋ':'â',
    'ᐍ':'wê','ᐏ':'wi','ᐑ':'wî','ᐓ':'wo','ᐕ':'wô','ᐘ':'wa','ᐚ':'wâ',
    'ᐯ':'pê','ᐱ':'pi','ᐲ':'pî','ᐳ':'po','ᐴ':'pô','ᐸ':'pa','ᐹ':'pâ','ᑊ':'p',
    'ᑌ':'tê','ᑎ':'ti','ᑏ':'tî','ᑐ':'to','ᑑ':'tô','ᑕ':'ta','ᑖ':'tâ','ᑦ':'t',
    'ᑫ':'kê','ᑭ':'ki','ᑮ':'kî','ᑯ':'ko','ᑰ':'kô','ᑲ':'ka','ᑳ':'kâ','ᒃ':'k',
    'ᒉ':'cê','ᒋ':'ci','ᒌ':'cî','ᒍ':'co','ᒎ':'cô','ᒐ':'ca','ᒑ':'câ','ᒡ':'c',
    'ᒣ':'mê','ᒥ':'mi','ᒦ':'mî','ᒧ':'mo','ᒨ':'mô','ᒪ':'ma','ᒫ':'mâ','ᒻ':'m',
    'ᓀ':'nê','ᓂ':'ni','ᓃ':'nî','ᓄ':'no','ᓅ':'nô','ᓇ':'na','ᓈ':'nâ','ᓐ':'n',
    'ᓭ':'sê','ᓯ':'si','ᓰ':'sî','ᓱ':'so','ᓲ':'sô','ᓴ':'sa','ᓵ':'sâ','ᔅ':'s',
    'ᔦ':'yê','ᔨ':'yi','ᔩ':'yî','ᔪ':'yo','ᔫ':'yô','ᔭ':'ya','ᔮ':'yâ','ᔾ':'y',
    'ᐍ':'wê','ᐏ':'wi','ᐑ':'wî','ᐓ':'wo','ᐕ':'wô','ᐘ':'wa','ᐚ':'wâ','ᐤ':'w',
    'ᐦ':'h','ᐧ':'w',
    // Moose Cree l-series
    'ᓕ':'le','ᓗ':'lo','ᓚ':'la','ᓪ':'l',
    // East Cree r-series
    'ᕃ':'re','ᕆ':'ri','ᕋ':'ra','ᕐ':'r',
    '᙮':'.',
  };

  // ── GLAS (Great Lakes Algonquian Syllabics) PUA codepoints ────────────────
  // Catrinity maps these in E480–E49F range.
  // GLAS was used primarily for Potawatomi (Catholic mission origins, 1830s–1900s).
  // The system is an alphasyllabary: consonant+vowel glyphs, not pure abjad.
  // Some Meskwaki (Fox/Sac) and early Kickapoo materials also used GLAS.
  //
  // Source: https://thelanguagecloset.com/2020/06/28/writing-in-north-america-great-lakes-algonquian-syllabics-glas/
  // Catrinity GLAS PUA mapping (approximate — verify against Catrinity docs):
  const GLAS_PUA = {
    // PUA codepoints E480–E49F → romanization (Potawatomi practical orthography)
    '\uE480': { rom: 'pa', ipa: 'pa',  note: 'GLAS pa (Potawatomi)' },
    '\uE481': { rom: 'pi', ipa: 'pi',  note: 'GLAS pi' },
    '\uE482': { rom: 'po', ipa: 'po',  note: 'GLAS po' },
    '\uE483': { rom: 'pe', ipa: 'pe',  note: 'GLAS pe' },
    '\uE484': { rom: 'ta', ipa: 'ta',  note: 'GLAS ta' },
    '\uE485': { rom: 'ti', ipa: 'ti',  note: 'GLAS ti' },
    '\uE486': { rom: 'to', ipa: 'to',  note: 'GLAS to' },
    '\uE487': { rom: 'te', ipa: 'te',  note: 'GLAS te' },
    '\uE488': { rom: 'ka', ipa: 'ka',  note: 'GLAS ka' },
    '\uE489': { rom: 'ki', ipa: 'ki',  note: 'GLAS ki' },
    '\uE48A': { rom: 'ko', ipa: 'ko',  note: 'GLAS ko' },
    '\uE48B': { rom: 'ke', ipa: 'ke',  note: 'GLAS ke' },
    '\uE48C': { rom: 'ma', ipa: 'ma',  note: 'GLAS ma' },
    '\uE48D': { rom: 'mi', ipa: 'mi',  note: 'GLAS mi' },
    '\uE48E': { rom: 'mo', ipa: 'mo',  note: 'GLAS mo' },
    '\uE48F': { rom: 'me', ipa: 'me',  note: 'GLAS me' },
    '\uE490': { rom: 'na', ipa: 'na',  note: 'GLAS na' },
    '\uE491': { rom: 'ni', ipa: 'ni',  note: 'GLAS ni' },
    '\uE492': { rom: 'no', ipa: 'no',  note: 'GLAS no' },
    '\uE493': { rom: 'ne', ipa: 'ne',  note: 'GLAS ne' },
    '\uE494': { rom: 'sa', ipa: 'sa',  note: 'GLAS sa' },
    '\uE495': { rom: 'si', ipa: 'si',  note: 'GLAS si (=sh in some dialects)' },
    '\uE496': { rom: 'so', ipa: 'so',  note: 'GLAS so' },
    '\uE497': { rom: 'se', ipa: 'se',  note: 'GLAS se' },
    '\uE498': { rom: 'ya', ipa: 'ja',  note: 'GLAS ya' },
    '\uE499': { rom: 'yi', ipa: 'ji',  note: 'GLAS yi' },
    '\uE49A': { rom: 'yo', ipa: 'jo',  note: 'GLAS yo' },
    '\uE49B': { rom: 'ye', ipa: 'je',  note: 'GLAS ye' },
    '\uE49C': { rom: 'wa', ipa: 'wa',  note: 'GLAS wa' },
    '\uE49D': { rom: 'wi', ipa: 'wi',  note: 'GLAS wi' },
    '\uE49E': { rom: 'wo', ipa: 'wo',  note: 'GLAS wo' },
    '\uE49F': { rom: 'we', ipa: 'we',  note: 'GLAS we' },
  };

  // Script detection: which rendering system does a text use?
  function detectScript(text) {
    if (!text) return 'roman';
    for (const ch of text) {
      const cp = ch.codePointAt(0);
      if (cp >= 0x1400 && cp <= 0x167F) return 'ucas';   // Cree syllabics
      if (cp >= 0x18B0 && cp <= 0x18FF) return 'ucas';   // UCAS Extended
      if (cp >= 0xE480 && cp <= 0xE49F) return 'glas';   // GLAS PUA (Catrinity)
    }
    return 'roman';
  }

  // ── Tokenizer (longest-match) ──────────────────────────────────────────────
  function tokenize(text, table) {
    const keys = Object.keys(table);
    const result = [];
    let i = 0;
    while (i < text.length) {
      let matched = false;
      for (const k of keys) {
        if (text.slice(i, i + k.length) === k) {
          result.push({ key: k, data: table[k] });
          i += k.length;
          matched = true;
          break;
        }
      }
      if (!matched) {
        result.push({ key: text[i], data: null });
        i++;
      }
    }
    return result;
  }

  // ── Text → IPA conversion ──────────────────────────────────────────────────
  function toIPA(text, lang) {
    const script = detectScript(text);
    let working = text;

    // UCAS → SRO first
    if (script === 'ucas') {
      working = [...text].map(ch => UCAS_TO_SRO[ch] || ch).join('');
      lang = 'cre';
    }
    // GLAS PUA → romanization first
    if (script === 'glas') {
      working = [...text].map(ch => GLAS_PUA[ch] ? GLAS_PUA[ch].rom : ch).join('');
      lang = 'pot';
    }

    const table = lang === 'mia' ? MIA_TO_IPA
                : lang === 'kic' ? KIC_TO_IPA
                : lang === 'cre' ? CREE_SRO_TO_IPA
                : MIA_TO_IPA;  // default

    return tokenize(working, table)
      .map(t => t.data ? (typeof t.data === 'string' ? t.data : t.data.ipa || t.key) : t.key)
      .join('');
  }

  // IPA → Italian-approximation string for SpeechSynthesisUtterance
  function ipaToItString(ipa) {
    const keys = Object.keys(IPA_TO_IT);
    let result = '';
    let i = 0;
    while (i < ipa.length) {
      let matched = false;
      for (const k of keys) {
        if (ipa.slice(i, i + k.length) === k) {
          result += IPA_TO_IT[k];
          i += k.length;
          matched = true;
          break;
        }
      }
      if (!matched) { result += ipa[i]; i++; }
    }
    return result;
  }

  // ── Voice selection ────────────────────────────────────────────────────────
  let _voiceCache = null;
  function getVoices() {
    if (_voiceCache) return _voiceCache;
    _voiceCache = window.speechSynthesis.getVoices();
    return _voiceCache;
  }
  // Browsers fire voiceschanged asynchronously
  window.speechSynthesis && window.speechSynthesis.addEventListener('voiceschanged', () => {
    _voiceCache = window.speechSynthesis.getVoices();
  });

  function findVoice(profile) {
    const voices = getVoices();
    // Try hint name first
    if (profile.voiceHint) {
      const byName = voices.find(v => v.name.includes(profile.voiceHint));
      if (byName) return byName;
    }
    // Fall back to any voice in the target language
    return voices.find(v => v.lang.startsWith(profile.lang.slice(0,5))) || null;
  }

  // ── Speech synthesis ──────────────────────────────────────────────────────
  /**
   * Speak a word in the given language.
   * @param {string} text      — orthographic form (any script)
   * @param {string} lang      — ISO 639-3 code: mia, kic, pot, sac, cre, sha
   * @param {string} [gender]  — 'male' | 'female' | 'neutral'
   * @param {string} [ipa]     — pre-computed IPA (skip conversion if provided)
   */
  function speak(text, lang, gender = 'neutral', ipa = null) {
    if (!CONFIG.ttsEnabled || !window.speechSynthesis) return;

    const profile = (PROFILES[lang] || PROFILES.mia)[gender] || PROFILES.mia.neutral;
    const ipaStr  = ipa || toIPA(text, lang);
    const itStr   = ipaToItString(ipaStr);
    const speakStr = itStr || text;  // fallback to original if conversion fails

    const utt = new SpeechSynthesisUtterance(speakStr);
    utt.lang  = profile.lang;
    utt.pitch = profile.pitch;
    utt.rate  = profile.rate;

    const voice = findVoice(profile);
    if (voice) utt.voice = voice;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utt);

    return { ipa: ipaStr, itApprox: itStr, profile };
  }

  /**
   * Speak from a corpus entry object.
   * Uses stored IPA directly if available (no re-conversion).
   */
  function speakEntry(entry, gender = 'neutral') {
    return speak(entry.form, entry.lang, gender, entry.ipa || null);
  }

  // ── Tooltip / annotation rendering ────────────────────────────────────────
  /**
   * Wrap text in phoneme tooltip spans.
   * Used for search result cards and detail panel.
   * Returns HTML string with .ph spans.
   */
  function annotateText(text, lang) {
    if (!text) return '';
    const script = detectScript(text);
    let table;

    if (script === 'ucas') {
      table = UCAS_TO_SRO;  // syllabic → SRO tooltip
      return annotateUCAS(text);
    }
    if (script === 'glas') {
      return annotateGLAS(text);
    }

    // Roman script — use language-specific table
    table = lang === 'mia' ? MIA_TO_IPA
          : lang === 'kic' ? KIC_TO_IPA
          : lang === 'cre' ? CREE_SRO_TO_IPA
          : MIA_TO_IPA;

    const keys = Object.keys(table);
    let out = '';
    let i = 0;
    while (i < text.length) {
      let matched = false;
      for (const k of keys) {
        if (text.slice(i, i + k.length) === k) {
          const ipa = typeof table[k] === 'string' ? table[k] : (table[k].ipa || k);
          out += phonemeSpan(k, null, ipa, lang);
          i += k.length;
          matched = true;
          break;
        }
      }
      if (!matched) { out += eh(text[i]); i++; }
    }
    return out;
  }

  function annotateUCAS(text) {
    return [...text].map(ch => {
      const sro = UCAS_TO_SRO[ch];
      if (!sro) return eh(ch);
      // Build IPA from SRO
      const ipa = tokenize(sro, CREE_SRO_TO_IPA).map(t => t.data || t.key).join('');
      return phonemeSpan(ch, sro, ipa, 'cre');
    }).join('');
  }

  function annotateGLAS(text) {
    return [...text].map(ch => {
      const d = GLAS_PUA[ch];
      if (!d) return eh(ch);
      return phonemeSpan(ch, d.rom, d.ipa, 'pot', d.note);
    }).join('');
  }

  function phonemeSpan(glyph, rom, ipa, lang, extra = '') {
    const romStr  = rom  ? `<span class="tip-rom">${eh(rom)}</span> ` : '';
    const ipaStr  = ipa  ? `<span class="tip-ipa">/${eh(ipa)}/</span> ` : '';
    const noteStr = extra ? `<span class="tip-note">${eh(extra)}</span>` : '';
    const ttsBtn  = `<span class="tip-tts" onclick="event.stopPropagation();Kilahkwaani.speak('${escAttr(glyph)}','${lang}','neutral')" title="Listen">🔊</span>`;
    return `<span class="ph" tabindex="0" role="button" aria-label="${rom||glyph}">${eh(glyph)}<span class="tip">${romStr}${ipaStr}${noteStr}${ttsBtn}</span></span>`;
  }

  function eh(s)       { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function escAttr(s)  { return String(s||'').replace(/'/g,"\\'").replace(/"/g,'&quot;'); }

  // ── SRO ↔ Syllabics toggle ─────────────────────────────────────────────────
  // Builds a reverse map: SRO → UCAS character
  const SRO_TO_UCAS = {};
  for (const [syl, sro] of Object.entries(UCAS_TO_SRO)) {
    if (!SRO_TO_UCAS[sro]) SRO_TO_UCAS[sro] = syl;
  }

  /**
   * Convert SRO romanization to UCAS syllabics display.
   * Used when a Cree entry is stored as SRO in the DB
   * but user has enabled syllabics display mode.
   */
  function sroToSyllabics(sro) {
    // Sort keys by length desc for longest-match
    const keys = Object.keys(SRO_TO_UCAS).sort((a,b) => b.length - a.length);
    let out = '';
    let i = 0;
    while (i < sro.length) {
      let matched = false;
      for (const k of keys) {
        if (sro.slice(i, i+k.length) === k) {
          out += SRO_TO_UCAS[k];
          i += k.length;
          matched = true;
          break;
        }
      }
      if (!matched) { out += sro[i]; i++; }
    }
    return out;
  }

  // State: syllabics display mode per language
  const _syllabicsMode = { cre: false, pot: false };

  function toggleSyllabics(lang) {
    _syllabicsMode[lang] = !_syllabicsMode[lang];
    return _syllabicsMode[lang];
  }

  function isSyllabicsMode(lang) {
    return !!_syllabicsMode[lang];
  }

  // ── Font loading ───────────────────────────────────────────────────────────

  /**
   * Inject CSS @font-face rules and Google Fonts link.
   * Call once during init.
   */
  function injectFontCSS(config) {
    const style = document.createElement('style');
    style.id = 'kilahkwaani-fonts';
    style.textContent = `
/* ── Catrinity: UCAS + GLAS PUA + IPA ─────────────────────────────────── */
@font-face {
  font-family: 'Catrinity';
  src: url('${config.catrinityPath}') format('opentype');
  /* Serve Catrinity ONLY for these blocks — saves bandwidth */
  unicode-range:
    U+1400-167F,    /* UCAS (Cree syllabics, GLAS Cree-based) */
    U+18B0-18FF,    /* UCAS Extended */
    U+E480-E49F,    /* GLAS PUA (Potawatomi, Fox, Kickapoo legacy) */
    U+0250-02AF,    /* IPA Extensions */
    U+0300-036F;    /* Combining Diacritical Marks */
  font-display: swap;
}

/* CatrinityFlags — special symbols, clan/nation markers */
@font-face {
  font-family: 'CatrinityFlags';
  src: url('${config.catrinityFlagsPath}') format('opentype');
  unicode-range: U+E000-E47F;   /* PUA — Catrinity flag glyphs */
  font-display: swap;
}

/* BJ Cree (Google Fonts) — high-quality typographic Cree syllabics */
/* Loaded via <link> if googleFontsEnabled; this is the fallback rule */
@font-face {
  font-family: 'BJ Cree';
  font-display: swap;
}

/* Script-specific font stacks */
.script-ucas {
  font-family: 'BJ Cree', 'Noto Sans Canadian Aboriginal', 'Catrinity', sans-serif;
  font-size: 1.15em;
  line-height: 1.4;
}
.script-glas {
  font-family: 'Catrinity', 'Noto Sans Canadian Aboriginal', sans-serif;
  font-size: 1.15em;
}
.script-roman {
  /* inherits body font (IM Fell English or similar) */
}

/* Language-specific class applied to .entry-card, .hw, .ph spans */
[lang="cre"] .hw, .hw[data-lang="cre"],
[lang="csw"] .hw, .hw[data-lang="csw"] {
  font-family: 'BJ Cree', 'Noto Sans Canadian Aboriginal', 'Catrinity', sans-serif;
}

[lang="pot"] .hw[data-script="glas"], .hw[data-lang="pot"][data-script="glas"] {
  font-family: 'Catrinity', 'Noto Sans Canadian Aboriginal', sans-serif;
}

/* IPA in tooltips */
.tip-ipa {
  font-family: 'Catrinity', 'Noto Sans Canadian Aboriginal',
               'Segoe UI', system-ui, sans-serif;
  color: #7eb8a4;
}
.tip-rom  { color: #c8a96e; font-weight: 600; }
.tip-note { color: #9a9080; font-size: .9em; }
.tip-tts  {
  cursor: pointer; margin-left: .3em; opacity: .7;
  transition: opacity .15s;
  font-style: normal;
}
.tip-tts:hover { opacity: 1; }

/* TTS speak button on cards */
.speak-btn {
  display: inline-flex; align-items: center; gap: .3em;
  background: none; border: 1px solid currentColor;
  border-radius: 3px; padding: .1em .4em;
  font-size: .72rem; cursor: pointer; opacity: .65;
  transition: opacity .15s;
  font-family: var(--mono, monospace);
}
.speak-btn:hover { opacity: 1; }

/* Syllabics toggle button */
.syl-toggle {
  font-family: 'BJ Cree', 'Noto Sans Canadian Aboriginal', sans-serif;
  font-size: .85em;
  border: 1px dashed currentColor; border-radius: 3px;
  padding: .1em .4em; cursor: pointer; opacity: .7;
}
.syl-toggle.active { opacity: 1; font-weight: bold; }

/* GLAS display notice */
.glas-notice {
  font-size: .72rem; font-family: var(--mono, monospace);
  color: #9a6e1a; background: rgba(154,110,26,.08);
  border: 1px solid rgba(154,110,26,.25);
  border-radius: 3px; padding: .2em .5em;
  display: inline-block; margin-left: .5em;
}
`;
    document.head.appendChild(style);

    // Google Fonts link (BJ Cree + Noto Sans Canadian Aboriginal)
    if (config.googleFontsEnabled) {
      // Check if already loaded
      if (!document.querySelector('link[href*="BJ+Cree"]')) {
        const link = document.createElement('link');
        link.rel  = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=BJ+Cree:wght@400;500;600;700'
                  + '&family=Noto+Sans+Canadian+Aboriginal:wght@100..900'
                  + '&display=swap';
        document.head.appendChild(link);
      }
    }
  }

  // ── Catrinity subsetting via opentype.js ───────────────────────────────────
  /**
   * Load Catrinity.otf and export a subset containing only Algic-relevant
   * Unicode blocks. Downloads the trimmed font automatically.
   * Requires opentype.js to be loaded and CORS-accessible font file.
   */
  function subsetCatrinity(otfPath, callback) {
    if (typeof opentype === 'undefined') {
      console.warn('[Kilahkwaani] opentype.js not loaded — subsetting unavailable');
      return;
    }

    const RANGES = [
      [0x1400, 0x167F],   // UCAS
      [0x18B0, 0x18FF],   // UCAS Extended
      [0xE480, 0xE49F],   // GLAS PUA
      [0x0250, 0x02AF],   // IPA Extensions
      [0x0300, 0x036F],   // Combining Diacritical Marks
      [0x0020, 0x007E],   // Basic Latin (keep ASCII)
    ];

    opentype.load(otfPath, (err, font) => {
      if (err) { console.error('[Kilahkwaani] Catrinity load error:', err); return; }

      const glyphs = [font.glyphs.get(0)];  // .notdef always first
      for (const [start, end] of RANGES) {
        for (let cp = start; cp <= end; cp++) {
          const g = font.charToGlyph(String.fromCodePoint(cp));
          if (g && g.index !== 0) glyphs.push(g);
        }
      }

      // Deduplicate
      const seen = new Set();
      const unique = glyphs.filter(g => {
        if (seen.has(g.index)) return false;
        seen.add(g.index); return true;
      });

      const subset = new opentype.Font({
        familyName: 'Catrinity-Algic',
        styleName:  'Regular',
        unitsPerEm: font.unitsPerEm,
        ascender:   font.ascender,
        descender:  font.descender,
        glyphs:     unique,
      });

      if (callback) {
        callback(subset);
      } else {
        subset.download('Catrinity-Algic.otf');
        console.log(`[Kilahkwaani] Catrinity subset: ${unique.length} glyphs (was ${font.glyphs.length})`);
      }
    });
  }

  // ── Font readiness check ───────────────────────────────────────────────────
  function checkFonts() {
    const tests = [
      { family: 'BJ Cree',                     test: 'ᓂ' },
      { family: 'Noto Sans Canadian Aboriginal', test: 'ᑭ' },
      { family: 'Catrinity',                    test: '\uE480' },
    ];

    const results = {};
    Promise.allSettled(
      tests.map(t =>
        document.fonts.load(`1em "${t.family}"`)
          .then(() => { results[t.family] = true;  })
          .catch(() => { results[t.family] = false; })
      )
    ).then(() => {
      console.log('[Kilahkwaani] Font status:', results);
      document.body.setAttribute('data-fonts-ready',
        Object.values(results).some(Boolean) ? 'partial' : 'none');
      document.body.dispatchEvent(new CustomEvent('kilahkwaani:fonts-ready', { detail: results }));
    });
  }

  // ── DOM helpers: inject TTS button into entry cards ───────────────────────
  /**
   * Add a 🔊 speak button to an existing card element.
   * @param {HTMLElement} el    — the .entry-card or any container
   * @param {string} form       — the word to speak
   * @param {string} lang       — language code
   * @param {string} [ipa]      — pre-computed IPA (optional)
   */
  function addSpeakButton(el, form, lang, ipa = '') {
    const btn = document.createElement('button');
    btn.className = 'speak-btn';
    btn.title = `Hear "${form}" in ${lang}`;
    btn.innerHTML = '🔊 <span class="speak-label">listen</span>';
    btn.setAttribute('data-form', form);
    btn.setAttribute('data-lang', lang);
    btn.onclick = (e) => {
      e.stopPropagation();
      const result = speak(form, lang, 'neutral', ipa || null);
      if (result) btn.title = `IPA: /${result.ipa}/`;
    };
    el.appendChild(btn);
    return btn;
  }

  /**
   * Add syllabics toggle button for Cree/Potawatomi cards.
   * Toggles between SRO roman and UCAS/GLAS display.
   */
  function addSyllabicsToggle(el, form, lang, hwEl) {
    if (!['cre','csw','pot'].includes(lang)) return;
    const btn = document.createElement('button');
    btn.className = 'syl-toggle';
    btn.title = lang === 'cre' ? 'Toggle syllabics ↔ SRO' : 'Toggle GLAS ↔ roman';
    btn.textContent = lang === 'cre' ? 'ᓂ' : '\uE480';  // preview glyph
    btn.onclick = (e) => {
      e.stopPropagation();
      const nowSyl = toggleSyllabics(lang);
      btn.classList.toggle('active', nowSyl);
      if (hwEl) {
        if (nowSyl && lang === 'cre') {
          // SRO → syllabics
          const syllabic = sroToSyllabics(form);
          hwEl.innerHTML = annotateUCAS(syllabic);
          hwEl.setAttribute('data-script', 'ucas');
          hwEl.classList.add('script-ucas');
        } else {
          hwEl.innerHTML = annotateText(form, lang);
          hwEl.removeAttribute('data-script');
          hwEl.classList.remove('script-ucas');
        }
      }
    };
    el.appendChild(btn);
    return btn;
  }

  // ── GLAS display notice ────────────────────────────────────────────────────
  function glasNotice() {
    const span = document.createElement('span');
    span.className = 'glas-notice';
    span.title = 'Great Lakes Algonquian Syllabics (GLAS) — requires Catrinity font';
    span.textContent = 'GLAS';
    return span;
  }

  // ── Public init ────────────────────────────────────────────────────────────
  function init(userConfig = {}) {
    Object.assign(CONFIG, userConfig);
    injectFontCSS(CONFIG);
    checkFonts();

    // Subsetting on demand (only if requested and opentype.js present)
    if (CONFIG.subsettingEnabled) {
      window.addEventListener('load', () => {
        subsetCatrinity(CONFIG.catrinityPath);
      });
    }

    console.log('[Kilahkwaani v2] Initialised —',
                'Catrinity:', CONFIG.catrinityPath,
                '| TTS:', CONFIG.ttsEnabled,
                '| Fonts:', CONFIG.googleFontsEnabled ? 'Google+local' : 'local only');
  }

  // ── Public API ─────────────────────────────────────────────────────────────
  return {
    init,
    speak,
    speakEntry,
    annotateText,
    annotateUCAS,
    annotateGLAS,
    addSpeakButton,
    addSyllabicsToggle,
    sroToSyllabics,
    toggleSyllabics,
    isSyllabicsMode,
    detectScript,
    toIPA,
    subsetCatrinity,
    glasNotice,

    // Expose tables for external use / extension
    tables: {
      MIA_TO_IPA, KIC_TO_IPA, CREE_SRO_TO_IPA,
      UCAS_TO_SRO, SRO_TO_UCAS, GLAS_PUA,
      IPA_TO_IT, PROFILES,
    },

    // Config accessor
    config: () => ({ ...CONFIG }),
  };

})();

// ═══════════════════════════════════════════════════════════════════════════
// INTEGRATION PATCH for algic_ety_applet_v3.py
// ═══════════════════════════════════════════════════════════════════════════
/**
 * Patch the applet's annotate() function to use Kilahkwaani instead.
 * Call after DOM ready if inlining this file in the Flask template.
 *
 * The applet already has:
 *   function annotate(text, lang) { ... }
 *   function renderRes(rows) { ... }
 *   async function loadDet(word, lang) { ... }
 *
 * This patch replaces annotate() and enriches renderRes() cards
 * with speak buttons and syllabics toggles.
 */
function patchApplet() {
  // Replace the applet's annotate() with Kilahkwaani's version
  if (typeof window.annotate === 'function') {
    window.annotate = (text, lang) => Kilahkwaani.annotateText(text, lang);
    console.log('[Kilahkwaani] Patched applet annotate()');
  }

  // Intercept card rendering to add speak buttons
  const _origRenderRes = window.renderRes;
  if (typeof _origRenderRes === 'function') {
    window.renderRes = function(rows) {
      _origRenderRes(rows);
      // After DOM update, add speak buttons and syllabics toggles
      requestAnimationFrame(() => {
        document.querySelectorAll('.entry-card[data-form]').forEach(card => {
          const form = card.getAttribute('data-form');
          const lang = card.getAttribute('data-lang');
          const ipa  = card.getAttribute('data-ipa') || '';
          const hwEl = card.querySelector('.hw');
          Kilahkwaani.addSpeakButton(card, form, lang, ipa);
          Kilahkwaani.addSyllabicsToggle(card, form, lang, hwEl);
        });
      });
    };
  }

  // Add data-attributes to cards (requires template modification — see below)
  // Template change needed in renderRes():
  //   <div class="entry-card"
  //        data-form="${r.form}"
  //        data-lang="${r.lang}"
  //        data-ipa="${r.ipa||''}"
  //        onclick="loadDet(...)">
}

// Auto-patch if applet globals detected
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    Kilahkwaani.init({
      catrinityPath:      '/static/Catrinity.otf',
      catrinityFlagsPath: '/static/CatrinityFlags.otf',
      googleFontsEnabled: true,
      ttsEnabled:         true,
    });
    // Delay patch to allow applet JS to define its functions
    setTimeout(patchApplet, 100);
  });
}
