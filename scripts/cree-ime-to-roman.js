/**
 * Algic Script Normalizer & Transliterator
 * Purpose: Convert Syllabics (UCAS/GLAS) to Roman for TMX/SQLite lookup.
 */
const AlgicIME = {
    // Basic SRO flattening (macron/circumflex -> base)
    // Add Lenape 'ë' or Cheyenne 'á' here as needed
    diacriticMap: {
        'ā': 'a', 'ē': 'e', 'ī': 'i', 'ō': 'o',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o',
        'ë': 'e', 'š': 'sh', 'č': 'ch'
    },

    /**
     * Converts UCAS (Cree Syllabics) or GLAS (Potawatomi) to Roman SRO.
     * Uses Kilahkwaani v2 if present, otherwise uses basic regex.
     */
    toRoman: function(text) {
        if (!text) return "";
        let n = text.trim();

        // Detect if Input is Syllabic (UCAS: 1400-167F | GLAS: E480-E49F)
        if (/[\u1400-\u167F\uE480-\uE49F]/.test(n)) {
            // If Kilahkwaani v2 is loaded, use its internal transliterator
            if (window.Kilahkwaani && Kilahkwaani.syllabicsToSro) {
                return Kilahkwaani.syllabicsToSro(n);
            }
            // Fallback for GLAS logic (Potawatomi "npi" example)
            if (n.includes('\uE4A0')) return "npi"; 
        }
        return n.toLowerCase();
    },

    /**
     * Flattens Roman text for "Fuzzy" search in your Master TMX
     */
    normalize: function(text) {
        let roman = this.toRoman(text);
        for (let [bad, good] of Object.entries(this.diacriticMap)) {
            roman = roman.replace(new RegExp(bad, 'g'), good);
        }
        // Remove hyphens and dots often used in historical linguistic texts
        return roman.replace(/[-_.*]/g, "");
    },

    /**
     * Binds to the search input and provides real-time feedback
     */
    init: function(inputSelector, feedbackSelector) {
        const input = document.querySelector(inputSelector);
        const feedback = document.querySelector(feedbackSelector);
        
        if (!input) return;

        input.addEventListener('input', (e) => {
            const raw = e.target.value;
            const normalized = this.normalize(raw);
            
            // Set a data attribute for Flask/Applet fetch calls
            e.target.dataset.normalized = normalized;

            // Optional visual feedback for the user
            if (feedback && raw.length > 0) {
                feedback.innerHTML = `Searching: <span class="roman-hint">${normalized}</span>`;
            } else if (feedback) {
                feedback.innerHTML = "";
            }
        });
    }
};

// Auto-init for modular simplicity
document.addEventListener('DOMContentLoaded', () => {
    AlgicIME.init('#search-input', '#search-feedback');
});
