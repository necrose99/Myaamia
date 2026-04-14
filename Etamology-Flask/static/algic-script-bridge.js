/**
 * Algic Script Bridge
 * Handles side-by-side rendering for GLAS (Historical) and UCAS (Active).
 */
const AlgicBridge = {
    // Basic SRO to UCAS (Cree Syllabics) Logic
    sroToCree: function(text) {
        if (window.Kilahkwaani && Kilahkwaani.sroToSyllabics) {
            return Kilahkwaani.sroToSyllabics(text);
        }
        return text; 
    },

    // SRO to GLAS (Historical Great Lakes Syllabics)
    // Adjusts for Kickapoo/Fox variants if specified
    sroToGlas: function(text, lang) {
        if (window.Kilahkwaani && Kilahkwaani.romanToGlas) {
            return Kilahkwaani.romanToGlas(text, lang);
        }
        return text;
    },

    // The Normalizer for the Search IME
    normalizeInput: function(input) {
        let n = input.toLowerCase().trim();
        // If user types Syllabics, convert to Roman for TMX lookup
        if (/[\u1400-\u167F\uE480-\uE49F]/.test(n)) {
            if (window.Kilahkwaani) n = Kilahkwaani.syllabicsToSro(n);
        }
        // Flatten macrons/circumflexes (î -> i)
        return n.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/š/g, "sh");
    }
};
