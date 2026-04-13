# Myaamiaataweenki Etymology Explorer (v3)
### Comparative Algic Linguistics & Revitalization Workbench
**Status:** *Work in Progress / Research Prototype*
## 📜 Project Vision
The **Myaamiaataweenki Etymology Explorer** is a full-stack toolset designed to parse, compare, and visualize the Miami-Illinois language (*Myaamia*) alongside its kin—Kickapoo, Fox (Meskwaki), Shawnee, Potawatomi, and the reconstructed **Proto-Algonquian** ancestor.
By leveraging modern data formats like **TMX** and **LIFT**, this applet allows researchers and language learners to see how a word like *Kinoonke* (in deep water) shifts across geography and time. It serves as both a serious research tool for historical linguistics and a Rapid Application Development (RAD) platform for community revival efforts.
## 🛠 Technical Architecture
The system is built on a modular "Python-Backend / JavaScript-Client" architecture to ensure linguistic metadata (like IPA) remains separate from standard orthographies.
 * **Backend:** Python 3 / Flask
 * **Linguistic Processing:** ety, pyglossary, translate-toolkit, and Saxon-Che (XSLT 2.0).
 * **Data Sources:** TMX, LIFT, XLIFF, and Wiktionary Proto-Algonquian scrapes.
 * **Rendering Engine:** kilahkwaani_v2.js (Handles GLAS, UCAS, and Web Speech API).
 * **Fonts:** Noto Sans Canadian Aboriginal (Cree) and Catrinity (GLAS/Historical Syllabics).
## 🧬 Comparative Features
### 1. Script Synthesis & IME
The applet provides side-by-side rendering of different writing systems used across the Algic family:
 * **Modern SRO:** Standard Roman Orthography for Cree and Myaamia.
 * **UCAS:** Unified Canadian Aboriginal Syllabics for Northern relatives.
 * **GLAS (Archives):** Historical Great Lakes Algonquian Syllabics used in archival Kickapoo, Fox, and Potawatomi texts.
### 2. IPA Enrichment Pipeline
To support speech synthesis without "polluting" standard spelling, we use an enrichment script to tuck IPA data into TMX prop or comment fields:
 * **Automatic IPA Mapping:** Converts Roman SRO to IPA based on language-specific phonology.
 * **Phonetic Meta-data:** Stores vowel length, tone (Cheyenne), and syncope (Potawatomi).
### 3. Accessible Speech (TTS)
Using the Web Speech API with an "Italian-mapping" strategy for Algonquian vowels:
 * **Gender-Specific Scripting:** Support for Male/Female voice profiles.
 * **Frequency Adjustments:** Extensible JS templates to accommodate users with specific hearing range needs (deafness/hard of hearing).

adding more voice styles is easily done via Java scripts... 
## 📂 Repository Structure
```bash
├── algic_ety_applet_v3.py   # Main Flask Server & DB Logic
├── build.py                  # Modular HTML Concatenator
├── static/
│   ├── kilahkwaani_v2.js     # Font/Speech Engine
│   ├── Catrinity.otf         # GLAS Historical Font
│   └── applet.css            # Parchment/Historical Theme
├── templates/
│   ├── header.html           # Google Fonts & CSS Imports
│   └── footer.html           # Engine Initialization
└── data/
    ├── Algic_Master.tmx      # Multi-tribe Comparative Corpus
    └── Ilda-myaamia.tmx      # Myaamia-specific Data

```
## 🚀 Getting Started
### Prerequisites
 * Python 3.8+
 * pip install flask ety pyglossary saxonche lxml
 * Catrinity Font (placed in /static)
### Data Ingest
 1. Place your TMX files in the data directory.
 2. Run the enrichment script to generate x-ipa properties.
 3. Initialize the SQLite database via the Admin API.
### Build the Modular Client
If you are modifying the JS/CSS components, use the build script to generate the standalone applet:
```bash
python3 build.py

```
## 🤝 Community & Acknowledgments
 * **Historical Research:** Based on the work of David Costa, Leonard, and Voorhis.
 * ILDA-MYAAMIA DICTIONARY of which i have painstakingly scraped into a TMX and other formats...
 *  * **XSLT Bindings:** Myaamia XSLT Library.
 * **RAD Prototypes:** Developed with assistance from AI for rapid UI iteration.
*Mihšii Neewe — For the revival of our kindred voices.*


### 📝 Footnote Addition for README.md
> **Note on Extensibility:** > This architecture is designed to be highly extensible. Integrating a new language—ranging from the complex consonant clusters of **Blackfoot** to the nasalized vowels of **Lenape**—requires only a TMX import and a corresponding JavaScript mapping for Text-to-Speech (TTS).
> Because the system uses **ISO/Gothenburg codes** as keys, the client-side logic can dynamically swap morphologies. This allows for rapid comparative study between "kindred neighbors" (like Fox and Kickapoo) or distant relatives (like the Plains or Eastern branches) without modifying the core Python backend. Be it for archival recovery or modern community use, the modular JS templates allow for easy appending of new voice types, script variants, and accessibility profiles.
> 
### 🚀 Implementation Tip for the "Extensible" Goal
Since you mentioned **Blackfoot** and **Lenape**, you might want to add these placeholders to your MAPS in kilahkwaani_v2.js to truly make it "plug-and-play":
```javascript
// Add to Kilahkwaani.tables
TABLES: {
    // Blackfoot: Handling pre-aspiration and glottal stops
    BFT_TO_IPA: { "'": "ʔ", "hk": "ʰk", "hp": "ʰp", "ht": "ʰt", "ks": "ks" },
    
    // Lenape: Handling the schwa and voicing
    UNM_TO_IPA: { "ë": "ə", "š": "ʃ", "č": "tʃ", "x": "x" }
}

```

### 📝 Footnote/Synopsis Update for README.md
> **Future Roadmap: SIL EAF Integration**
> While TMX/LIFT provide the structural backbone for comparative study, the system is designed to eventually ingest **SIL EAF (ELAN)** files. EAF data allows for superior TTS rendering by capturing nuances that standard IPA hinting often misses, such as:
>  * **Allophonic Variation:** Subtle sound changes based on neighboring words.
>  * **Pitch & Timbre:** Essential for tonal languages like Cheyenne or the melodic contour of Myaamia speech.
>  * **Fricative Nuance:** Precise control over breathy or aspirated consonants.
> By bridging ELAN's time-aligned phonetic data with the JS client-side renderer, the applet can move beyond robotic synthesis toward a more "human-centric" vocal restoration.
> 
### 🛠️ Technical Context (For your JS/Python bridge)
Since you are already using **Saxon-Che** for XSLT in algic_ety_applet_v3.py, you are perfectly positioned to handle this. ELAN files are XML-based, meaning you can write an XSLT to extract the TIME_SLOT and ANNOTATION_VALUE directly into your SQLite prop field.
**How this improves your TTS (The "Nuance" layer):**
Standard IPA in your kilahkwaani_v2.js treats words as isolated blocks. EAF data allows your JS to adjust the speechSynthesisUtterance properties dynamically:
 1. **utterance.rate**: Adjusted by the time-duration of the EAF annotation.
 2. **utterance.pitch**: Adjusted by pitch-tier data extracted from the EAF.
 3. **utterance.volume**: Controlled by the stress markers in the ELAN file.
### 💡 Why this matters for RAD
Using AI to prototype the **EAF-to-TMX** converter means you can take decades of existing ELAN field recordings and "refill" your applet with authentic tribal voices. It changes the app from a "translator" into a "performer" of the language.
This synopsis effectively invites collaboration from field linguists who have hard drives full of ELAN data but no way to make it "speak" in a user-friendly app. It’s a very strong finishing touch for your documentation!
