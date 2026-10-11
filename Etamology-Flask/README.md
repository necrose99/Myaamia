# Myaamiaataweenki Etymology Explorer (v3)
### Comparative Algic Linguistics & Revitalization Workbench

**Status:** *Work in Progress / Research Prototype*

## 📜 Project Vision
The **Myaamiaataweenki Etymology Explorer** is a full-stack toolset designed to parse, compare, and visualize the Miami-Illinois language (*Myaamia*) alongside its kin—Kickapoo, Fox (Meskwaki), Shawnee, Potawatomi, and the reconstructed **Proto-Algonquian** ancestor.

By leveraging modern data formats like **TMX** and **LIFT**, this applet allows researchers and language learners to see how a word like *Kinoonke* (in deep water) shifts across geography and time. It serves as both a serious research tool for historical linguistics and a Rapid Application Development (RAD) platform for community revival efforts.

## 🛠 Technical Architecture
The system is built on a modular "Python-Backend / JavaScript-Client" architecture to ensure linguistic metadata (like IPA) remains separate from standard orthographies.

 * **Backend Platform:** Python 3 / Flask Core Server
 * **Pipeline Automation Engine:** `helpers/transmog.py` (decouples PyGlossary, Translate-Toolkit, and `rdflib` serialization).
 * **Linguistic Processing:** `ety`, `pyglossary`, `translate-toolkit`, and `saxonche` (XSLT 2.0).
 * **Data Sources:** TMX, LIFT, XLIFF, RDF Turtle (.ttl), and Wiktionary Proto-Algonquian scrapes.
 * **Rendering Engine:** `kilahkwaani_v2.js` (Handles GLAS, UCAS, and Web Speech API).
 * **Fonts:** Noto Sans Canadian Aboriginal (Cree) and Catrinity-GLAS (Web-optimized subsetted WOFF2).
 
 ## Quick Diagnostic Run Validation Pattern:Initialize Workspace: 
 Run just init to construct the isolated python runner boundary.Speed-up Setup:
 If a tester needs binary tools injected into their local context 
 without compiling source code, they can run just bootstrap to 
 deploy cargo-binstall instantly.Execute 8181 Engine: 
 Run just run to test your application safely over http://127.0.0.1:8181.
 
 
 https://github.com/cargo-bins/cargo-binstall/tree/main 
 cargo binstall just or  cargo install just
 https://github.com/casey/just/releases 
 just is much like unix  make  but dose deploypment jobs too..

## 📂 Repository Structure
```bash
Myaamia/
├── Algic-Etamology-Flask/     # Split Upstream Git Submodule Tier
│   ├── algic_ety_applet_v3.py # Main Flask Server & DB Logic
│   ├── build.py               # Web Font & HTML Concatenator Framework
│   ├── setup.py               # cx_Freeze Cross-Platform Toolchain Config
│   ├── pyproject.toml         # Hatch & hatch-cython Optimization Layout
│   ├── helpers/
│   │   ├── transmog.py        # Pipeline Engine & RDF Turtle Translator
│   │   ├── Myaamia2IPA.py     # Local Phoneme Transliteration Matrix
│   │   └── trim_font.py       # FontTools Subsetting Resource Component
│   └── conf/
│       └── Dockerfile         # Python 3 Alpine Production Layer
├── Etamology-Flask/           # Active Windows Junction Link (Symlink)
├── XSLT/linguistics-suite/xslt# Master Shared XSLT Workbench Matrix
├── scripts/                   # Local Dev Scripts (Md2tmx, LIFT2lemon)
├── justfile                   # Multi-Platform Test/Freeze Command Registry
├── deploy.sh                  # Container Engine Ingress Automator Script
└── docker-compose.yaml        # Multi-Container Persistent Storage Mapper
```

## 🧬 Comparative Features

### 1. Script Synthesis & IME
The applet provides side-by-side rendering of different writing systems used across the Algic family:
 * **Modern SRO:** Standard Roman Orthography for Cree and Myaamia.
 * **UCAS:** Unified Canadian Aboriginal Syllabics for Northern relatives.
 * **GLAS (Archives):** Historical Great Lakes Algonquian Syllabics used in archival Kickapoo, Fox, and Potawatomi texts. can toggel for that olde timiey feel

### 2. IPA Enrichment Pipeline
To support speech synthesis without "polluting" standard spelling, we use an enrichment script to tuck IPA data into TMX prop or comment fields:
 * **Automatic IPA Mapping:** Converts Roman SRO to IPA based on language-specific phonology.
 * **Phonetic Meta-data:** Stores vowel length, tone (Cheyenne), and syncope (Potawatomi).

### 3. Accessible Speech (TTS)
Using the Web Speech API with an "Italian-mapping" strategy for Algonquian vowels:
 * **Gender-Specific Scripting:** Support for Male/Female voice profiles.
 * **Frequency Adjustments:** Extensible JS templates to accommodate users with specific hearing range needs (deafness/hard of hearing). Adding more voice styles is easily done via client JavaScripts.

## 🚀 Local Development Workflow (`just`)
The repository includes a cross-platform toolchain (`justfile`) to facilitate local debugging, compiling, and frozen binary generation across Windows, Linux, and macOS.

* **Initialize Virtual Environment:** `just init` (creates Hatch workspace).
* **Launch Diagnostic Server:** `just run` (boots debug layout over local testing port **`8181`**).
* **Compile C-Extensions:** `just compile-c` (invokes `hatch-cython` high-performance builds).
* **Freeze Binary Distribution:** `just freeze` (compiles a standalone local package using `cx_Freeze`).

## 🔮 Future Roadmap: SIL EAF Integration
While TMX/LIFT provide the structural backbone for comparative study, the system is designed to eventually ingest **SIL EAF (ELAN)** files. EAF data allows for superior TTS rendering by capturing nuances that standard IPA hinting often misses, such as:
 * **Allophonic Variation:** Subtle sound changes based on neighboring words.
 * **Pitch & Timbre:** Essential for tonal languages like Cheyenne or the melodic contour of Myaamia speech.
 * **Fricative Nuance:** Precise control over breathy or aspirated consonants.

By bridging ELAN's time-aligned phonetic data with the JS client-side renderer via Saxon-CHE XSLT sheets, the applet can move beyond robotic synthesis toward a more "human-centric" vocal restoration, altering `speechSynthesisUtterance.rate` and `.pitch` dynamically to mirror historical field recordings.

## 📝 Note on Extensibility
This architecture is designed to be highly extensible. Integrating a new language—ranging from the complex consonant clusters of **Blackfoot** to the nasalized vowels of **Lenape**—requires only a TMX import and a corresponding JavaScript mapping for Text-to-Speech (TTS).

Because the system uses **ISO/Gothenburg codes** as keys, the client-side logic can dynamically swap morphologies. This allows for rapid comparative study between "kindred neighbors" (like Fox and Kickapoo) or distant relatives (like the Plains or Eastern branches) without modifying the core Python backend. Be it for archival recovery or modern community use, the modular JS templates allow for easy appending of new voice types, script variants, and accessibility profiles.

## ⚖️ Open Source & Extensibility
This project is distributed under the **MIT License**. The modular client architecture allows external teams, sovereign tribal nations, and digital humanities labs to extract code (like the `kilahkwaani_v2.js` rendering framework) to deploy directly on their own educational websites or digital dictionary portals.

## 🔮 Future Roadmap: Advanced Audio Ingress & Machine Learning
While text-to-speech serves as a vital rapid prototyping layout, the engine is designed to evolve its acoustic accuracy across three distinct diagnostic tiers:
1. **First-Order Audio Integration:** If participating university organizations or archival repositories supply a JSON URI schema pointing to field recordings, `kilahkwaani_v2.js` will automatically intercept the pipeline and execute the authentic **MP3 audio streams** as a first-order priority, preserving native cadence.
2. **Gruut IPA Processing:** To enhance backend data science workbenches, future updates will incorporate **Gruut IPA (Python)**. This enables programmatic text-to-phoneme tokenization, allowing the server to automatically insert accurate IPA symbols, aspiration variants, and glottal stops into input text vectors before sending them to the UI.
3. **Wav2Vec Acoustic Restoration:** To address the severe machine learning data scarcity surrounding endangered languages, the platform aims to integrate fine-tuned **Wav2Vec 2.0 / Wav2Vec-U** models. By leveraging unsupervised acoustic mapping against fragmentary, historic archival speech clips, the system can automatically adjust language morphology models—allowing *kilahkwaani* to dynamically self-correct its speech efforts over time.


*Mihšii Neewe — For the revival of our kindred voices.*
