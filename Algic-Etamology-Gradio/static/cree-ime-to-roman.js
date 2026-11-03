/**
 * cree-ime-to-roman.js — Comprehensive Algic Script Normalizer, Transliterator & IME Hooks
 * Integrates: Cree Syllabics (UCAS), Historical GLAS, and SRO Greedy Token Sorting.
 */

// Global runtime execution memory tables
let cachedCasMap = null;
let cachedSroMap = null;

const AlgicIME = {
    // Diacritic flattening dictionary maps for fuzzy Master TMX / SQLite indexing scans
    diacriticMap: {
        'ā': 'a', 'ē': 'e', 'ī': 'i', 'ō': 'o',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o',
        'ë': 'e', 'š': 'sh', 'č': 'ch', 'á': 'a'
    },

    /**
     * Streams and compiles upstream mapping dictionaries dynamically.
     * Drops raw JavaScript structural notation headers to build clean JSON.
     */
    initEngine: async function() {
        if (cachedCasMap && cachedSroMap) return; // Prevent loop reconstruction

        try {
            // 1. Fetch, clean, and sort Syllabics-to-Roman entries
            const casResponse = await fetch("https://githubusercontent.com");
            const casRawText = await casResponse.text();
            const processedCasText = casRawText.replace("var cas =", "").trim().replace(/;\$/, "");
            const parsedCasData = JSON.parse(processedCasText);
            
            // Greedy sorting: Longest glyph elements matched first to prevent compound token fragmentation
            cachedCasMap = [...parsedCasData].sort((a, b) => b.l.length - a.l.length);

            // 2. Fetch, clean, and sort SRO-to-Syllabics entries
            const sroResponse = await fetch("https://githubusercontent.com");
            const sroRawText = await sroResponse.text();
            const processedSroText = sroRawText.replace("var sro =", "").replace(/\/\/.*/gm, "").trim().replace(/;/, "");
            const parsedSroData = JSON.parse(processedSroText);

            let intermediateSroMap = {};
            parsedSroData.forEach(item => {
                if (item.l && item.t) intermediateSroMap[item.l] = item.t;
            });
            // Longest SRO tokens checked first to prevent shorter vowel collisions (e.g., "pwâ" before "p")
            cachedSroMap = Object.entries(intermediateSroMap).sort((a, b) => b[0].length - a[0].length);

            console.log("✔ Algic Upstream Transliteration Matrix parsed successfully.");
        } catch (err) {
            console.error("Upstream dictionary sync failed; fallback tracking activated: ", err);
            // Minimal critical fallback table state to keep basic lookups functional if GitHub is down
            cachedCasMap = [{"l":"ᐊ","t":"a"},{"l":"ᐋ","t":"â"},{"l":"ᐃ","t":"i"},{"l":"ᐄ","t":"î"}];
            cachedSroMap = [["â","ᐋ"],["a","ᐊ"],["î","ᐄ"],["i","ᐃ"]];
        }
    },

    /**
     * Syllabics (CAS/GLAS) to Roman SRO Transliterator Engine
     */
    toRoman: function(rawText) {
        if (!rawText) return "";
        let n = rawText.trim();

        // Detect if Input contains Syllabic Unicode blocks (UCAS: 1400-167F | GLAS PUA: E480-E49F)
        if (/[\u1400-\u167F\uE480-\uE49F]/.test(n)) {
            // Hook into Kilahkwaani v2 if present on your active global workspace
            if (window.Kilahkwaani && typeof Kilahkwaani.syllabicsToSro === 'function') {
                return window.Kilahkwaani.syllabicsToSro(n);
            }

            // Fallback for GLAS historical script logic (e.g., Potawatomi "npi" block)
            if (n.includes('\uE4A0')) return "npi";

            // Process via local engine map
            if (!cachedCasMap) return n.toLowerCase();
            let result = "";
            let offset = 0;
            while (offset < n.length) {
                let matchFound = false;
                for (let record of cachedCasMap) {
                    if (n.substr(offset, record.l.length) === record.l) {
                        result += record.t;
                        offset += record.l.length;
                        matchFound = true;
                        break;
                    }
                }
                if (!matchFound) {
                    result += n[offset];
                    offset++;
                }
            }
            return result;
        }
        return n.toLowerCase();
    },

    /**
     * Roman SRO to Syllabics (CAS) Transliterator Engine
     */
    toSyllabics: function(sroInput) {
        if (!sroInput || !cachedSroMap) return sroInput || "";
        let normalizedSro = sroInput.toLowerCase().trim();
        let result = "";
        let offset = 0;

        while (offset < normalizedSro.length) {
            let matchFound = false;
            for (let [sroToken, casGlyph] of cachedSroMap) {
                if (normalizedSro.substr(offset, sroToken.length) === sroToken) {
                    result += casGlyph;
                    offset += sroToken.length;
                    matchFound = true;
                    break;
                }
            }
            if (!matchFound) {
                result += normalizedSro[offset];
                offset++;
            }
        }
        return result;
    },

    /**
     * Flattens SRO variables for fuzzy Master TMX index scans
     */
    normalize: function(text) {
        let roman = this.toRoman(text);
        for (let [bad, good] of Object.entries(this.diacriticMap)) {
            roman = roman.replace(new RegExp(bad, 'g'), good);
        }
        // Remove hyphens, dots, and formatting characters common in historical texts
        return roman.replace(/[-_.*]/g, "");
    },

    /**
     * Binds input forms to real-time feedback panels
     */
    init: async function(inputSelector, feedbackSelector) {
        // Stream and register tracking metrics instantly at startup boundaries
        await this.initEngine();
        
        const input = document.querySelector(inputSelector);
        const feedback = document.querySelector(feedbackSelector);
        
        if (!input) return;

        input.addEventListener('input', (e) => {
            const raw = e.target.value;
            const normalized = this.normalize(raw);
            
            // Set dynamic element datasets for Flask database routing
            e.target.dataset.normalized = normalized;

            if (feedback && raw.length > 0) {
                feedback.innerHTML = `Normalized Search Target: <span class="roman-hint" style="color:#b58900; font-weight:bold;">${normalized}</span>`;
            } else if (feedback) {
                feedback.innerHTML = "";
            }
        });
    }
};

// Clean single entry automatic initialization boot hook
document.addEventListener('DOMContentLoaded', () => {
    AlgicIME.init('#search-input', '#search-feedback');
});
