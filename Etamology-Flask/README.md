Here is a comprehensive README.md drafted in professional Markdown. It synthesizes your project’s goals, the technical stack, and the linguistic vision for the Myaamia and broader Algic community.
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
 * **XSLT Bindings:** Myaamia XSLT Library.
 * **RAD Prototypes:** Developed with assistance from AI for rapid UI iteration.
*Mihšii Neewe — For the revival of our kindred voices.*
