/**
 * Kilahkwaani.js - The Speaker
 * A gender-aware phonetic synthesizer for Myaamia.
 */
const Kilahkwaani = {
    // Pitch/Rate profiles using Italian 'it-IT' for realistic Myaamia vowels
    profiles: {
        male:   { lang: 'it-IT', pitch: 0.80, rate: 0.85, name: 'Male' },
        female: { lang: 'it-IT', pitch: 1.15, rate: 0.95, name: 'Female' }
    },

    /**
     * @param {Object} wordData - The entry from myaamia_assets.json
     * @param {string} userPref - 'male' or 'female' from UI settings
     */
    speak: function(wordData, userPref = 'female') {
        const synth = window.speechSynthesis;
        
        // 1. GENDER ARBITRATION
        // If word is 'female' only (Naaka), force female. 
        // If 'male' only (Iihia), force male. Otherwise, use userPref.
        let activeGender = userPref;
        if (wordData.voice_profile !== "neutral") {
            activeGender = wordData.voice_profile;
            console.log(`[Kilahkwaani] Overriding to ${activeGender} for cultural accuracy.`);
        }

        const config = this.profiles[activeGender];

        // 2. AUDIO SOURCE SELECTION
        // If we have a recording AND the gender matches, play the MP3.
        // If it's a mismatch (Male MP3 for Naaka), use Synthesis.
        const isMismatch = wordData.has_recording && wordData.sample_gender !== activeGender;

        if (wordData.has_recording && !isMismatch) {
            const audio = new Audio(wordData.audio_url);
            audio.play();
        } else {
            // 3. SYNTHESIS FALLBACK
            const phoneticText = this.prepareIpaForEngine(wordData.ipa);
            const utterance = new SpeechSynthesisUtterance(phoneticText);
            
            const voices = synth.getVoices();
            utterance.voice = voices.find(v => v.lang === config.lang) || voices[0];
            utterance.pitch = config.pitch;
            utterance.rate = config.rate;

            synth.speak(utterance);
        }
    },

    prepareIpaForEngine: function(ipa) {
        return ipa.replace(/\//g, '')  // Strip /
                  .replace(/ʃ/g, 'sh') // Esh to sh
                  .replace(/aː/g, 'aa') // Long vowels
                  .replace(/ʰ/g, 'h');  // Pre-aspiration
    }
};
