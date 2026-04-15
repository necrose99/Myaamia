### Miami-Illinois (Myaamia) — necrose99/Myaamia
- [x] ILDA dictionary hand-scraped → TMX
      file: Myaamia-lda-dictionary.tmx
      status: partilty done — normalize and push to pipeline
- [x] Weblate memory exports
      files: *-weblate-memory.tmx
      status: DONE — merge and deduplicate
- [x] FLEx backup 2024-07-03
      file: Myaamia 2024-07-03 1957.fwbackup
      status: UNPROCESSED — extract LIFT, highest priority
- [x] OmegaT project
      dir: omegat/
      status: semi abandoned tool as its cumbersome to use without its plugins
      — export tm/*.tmx to pipeline

- [ ] ### Sac-Fox (Sauk)
- [ ] Community workbook PDF
      source: [url when found/confirmed]
      format: PDF interlinear → pdfplumber → LIFT
      parser: scrapy/sac_workbook_parser.py
      lang_code: sac
      orthography: practical-roman
      structure: 4-line interlinear (vernacular/morph/gloss/trans)
      est_entries: small — workbook scale ~200-500
      notes: table extraction first, line fallback second
             same parser reusable for kic

      # corpus_feeds.md
## Status: active | pending | requested | blocked

### Miami-Illinois
- [ ] ILAD deposits — hand-scrape in progress
      source: ailla.utexas.org
      format: HTML → LIFT
      orthography: costa-roman
      entries: ~2400 est.
      last_scraped: 2026-04-04

### Kickapoo  
- [ ] Voorhis manuscripts — Kansas archive request pending
      source: KU linguistics archive
      format: PDF → manual
      notes: Mexico variety priority if AILLA deposit exists

### Meskwaki
- [ ] NAA Michelson collection
      source: Smithsonian NAA digitized
      format: PDF interlinear → EAF
      orthography: bloomfield → fiero normalize first

### Wiktionary Proto-Algonquian
- [ ] etyl:alg tagged entries
      source: en.wiktionary.org/wiki/Category:Proto-Algonquian_reconstructions
      format: wikitext → DMLex etymonUnit JSON
      spider: scrapy/wiktionary_pa_spider.py
      api: api.php?action=parse&format=json

### Etymology cross-reference
- [ ] Wiktionary cognate chains
      target_table: cognate_set, cognate_member
      pipeline: wikitext → etymology_parser.py
SQLite middle layer buys you
EAF/LIFT → XSLT → normalized XML → SQLite staging tables
                                    ├── utterances
                                    ├── morphemes + glosses  
                                    ├── time_slots (for audio alignment)
                                    ├── etymology chains (DMLex)
                                    └── cross-reference pairs
                                              ↓
                                    Ollama fine-tuning corpus
The time_slot data from EAF is particularly valuable — it gives you ground-truth segmentation that most low-resource corpora lack entirely.
On the cross-pair gap
The missing French/English/Spanish parallel data is a real constraint, but the Algonquian language family has some under-used resources worth knowing about:
ALGONQUIAN-BASIC-VOCABULARY (Goddard) — digitized in some ELAR deposits
      Known solid sources worth targeting with scrapers:
Dictionaries / lexicons
Nishnaabemwin Reference Grammar (Valentine 2001) — the most comprehensive Ojibwe grammar, some digitized wordlists float around
The Ojibwe People's Dictionary (ojibwemowin.com) — University of Minnesota, openly accessible, has audio, structured entries, searchable — this is the crown jewel target
Freelang Ojibwe wordlist — small but clean, already tab-delimited
Weshki-ayaad Anishinaabe dictionary project — some CC-licensed exports
Parallel text
Anishinaabemodaa (anishinaabemodaa.ca) — bilingual Ojibwe/English stories, structured HTML, scrapeable
Ojibwe.net — phrase lists, some parallel structure
Project Gutenberg has a handful of 19th-century Ojibwe texts with English facing translation — Baraga's grammar/dictionary (1850) is PD, structured, and actually quite good morphologically
Institutionally accessible
OLAC-indexed deposits at AILLA and ELAR — requestable, some already have EAF with English translation tiers, which drops straight into your pipeline
ELDP (Endangered Language Documentation Programme) grant outputs — several Ojibwe/Anishnaabe projects deposited at SOAS
The orthography problem is real
Before any of that hits your regex layer you'll want a normalization pass. The double-vowel (Fiero) system is the modern standard but you'll encounter:
Fiero double-vowel:  aanii, miigwech, boozhoo
Syllabics:           ᐊᓂᐃ, ᒥᒋᐌᒡ
Bloomfield/older:    ânîi, mîgwec
Various mission:     ahnee, meegwetch
A pre-scrape orthography detector + normalizer to Fiero would pay dividends before anything touches the XSLT pipeline or SQLite. The langdetect + a small custom classifier on the vowel digraph patterns can get you 90%+ on that distinction programmatically.
Scraper priority order I'd suggest:
Ojibwe People's Dictionary first — structured, quality-controlled, audio-linked, University-maintained so unlikely to disappear
Anishinaabemodaa parallel stories — actual running text, not just wordlists
Baraga's dictionary via Gutenberg — morphologically rich, PD, consistent orthography within itself
OLAC deposit requests — slowest path but highest quality data
The OPD in particular has clean enough HTML structure that a requests + BeautifulSoup scraper feeding directly into LIFT XML via your generateDS bindings would be a natural first pipeline test on real data.
When you're ready to build it out, the scraper → LIFT → XSLT → SQLite → Ollama path is genuinely viable with what
you've already built.


Scraper priority order I'd suggest:
Ojibwe People's Dictionary first — structured, quality-controlled, audio-linked, University-maintained so unlikely to disappear
Anishinaabemodaa parallel stories — actual running text, not just wordlists
Baraga's dictionary via Gutenberg — morphologically rich, PD, consistent orthography within itself
OLAC deposit requests — slowest path but highest quality data
The OPD in particular has clean enough HTML structure that a requests + BeautifulSoup scraper feeding directly into LIFT XML via your generateDS bindings would be a natural first pipeline test on real data.
When you're ready to build it out, the scraper → LIFT → XSLT → SQLite → Ollama path is genuinely viable with what you've already built.

ILAD — absolutely primo. The International Languages of the Americas Database has rigorous linguistic annotation, consistent interlinear glossing, and a lot of it is already in formats close to what your XSLT suite expects. That's a different tier of data quality than scraped web text.
On Potawatomi and Sac (Sauk) — you're right about the indelibility
They're arguably more linguistically conservative in certain respects than the better-documented Ojibwe dialects:
Potawatomi retained the Proto-Algonquian *šk clusters and some morphophonological distinctions that Ojibwe leveled — so it's a better anchor point for reconstruction work
Sac-Fox (Meskwaki) is remarkable — the Meskwaki community in Tama, Iowa has maintained the language with unusual continuity, and there's a substantial manuscript tradition in the Meskwaki syllabary that's genuinely unique
Both have cleaner morpheme boundary behavior for the TI/TA/II/AI verb class system than the Ojibwe dialect continuum, which gets messy fast
Meskwaki specifically — the Smithsonian / NAA (National Anthropological Archives) has Truman Michelson's early 20th century Meskwaki collection, much of it interlinear, some digitized. That's PD and linguistically dense.
The comparative Algonquian angle
For your SQLite schema it's worth thinking about this now rather than retrofitting:
-- language node table
CREATE TABLE language (
    id          TEXT PRIMARY KEY,  -- ISO 639-3: ojp, pot, sac, cre...
    family      TEXT,              -- Algonquian
    subfamily   TEXT,              -- Central, Plains, Eastern
    orthography TEXT               -- fiero, syllabics, meskwaki-syllabary
);

-- cognate sets linking across languages
CREATE TABLE cognate_set (
    id           INTEGER PRIMARY KEY,
    proto_form   TEXT,             -- PA reconstruction
    proto_gloss  TEXT,
    confidence   REAL
);

CREATE TABLE cognate_member (
    cognate_set_id INTEGER REFERENCES cognate_set(id),
    language_id    TEXT REFERENCES language(id),
    surface_form   TEXT,
    source_ref     TEXT,           -- ILAD deposit ID, OPD entry, etc.
    lift_entry_id  TEXT            -- foreign key into your LIFT store
);
That structure lets Ollama do comparative inference across the family rather than treating each language as isolated — which for polysynthetic languages with shared morpheme inventories is where the classification payoff actually lives.
The Sac/Potawatomi/Ojibwe triangle as a training set with Meskwaki manuscript data as a high-quality anchor — that's a genuinely interesting corpus design. Not just linguistically defensible, it's the kind of thing that could produce a model that actually understands morpheme boundaries rather than pattern-matching on surface forms.
Worth the wait to do it right.



ILAD scrape → LIFT XML (generateDS) → lift-to-xliff.xsl → Weblate push API → done
The Weblate adapter's push_xliff() call handles the bulk upload. The painful part is the ILAD scraper that correctly captures the interlinear structure — but once that's written it runs unattended.
Miami-Illinois specific considerations
The language has some features that matter for your data model:
The Gatschet/Costa transcription vs. the modern Myaamia orthography are significantly different — same orthography normalization problem as Ojibwe but arguably more acute since the historical record is thinner
Miami-Illinois has the Algonquian polysynthetic verb morphology but with some unique reflexes of PA forms that are genuinely useful as comparative anchors
The Myaamia Center has been doing community-driven revitalization which means some of their materials have pedagogical glossing already — cleaner than raw fieldwork notes for training purposes
Scrapy spider sketch for ILAD
If the ILAD records have consistent URL patterns and HTML structure, a Scrapy spider feeding your LIFT bindings would look roughly like:
import scrapy
import sys
sys.path.insert(0, '../bindings')
import lift_ds

class ILADSpider(scrapy.Spider):
    name = "ilad_miami"
    
    # ILAD uses consistent record URLs
    start_urls = ["https://ailla.utexas.org/..."]  # adjust to actual ILAD endpoint
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,      # be polite
        'CONCURRENT_REQUESTS': 1,
        'ROBOTSTXT_OBEY': True,
    }

    def parse(self, response):
        # Extract interlinear fields — adjust selectors to actual ILAD HTML
        for record in response.css('div.record, tr.entry'):
            yield {
                'headword':    record.css('.headword, .form::text').get(''),
                'ipa':         record.css('.phonetic::text').get(''),
                'gloss_en':    record.css('.gloss-en::text').get(''),
                'gloss_fr':    record.css('.gloss-fr::text').get(''),
                'morph':       record.css('.morphemes::text').get(''),
                'example':     record.css('.example::text').get(''),
                'trans':       record.css('.translation::text').get(''),
                'source_ref':  record.css('.citation::text').get(''),
            }
        
        # Follow pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def closed(self, reason):
        # Could trigger LIFT export here
        pass
Then a Scrapy pipeline item processor:

class LIFTExportPipeline:
    """
    Scrapy item pipeline that accumulates scraped ILAD records
    and writes them to a LIFT 0.13 file via generateDS bindings.
    """

    def open_spider(self, spider):
        self.lift_root = lift_ds.lift()
        self.lift_root.set_version('0.13')
        self.lift_root.set_producer('ilad-scrapy-pipeline')
        self.entry_count = 0

    def process_item(self, item, spider):
        entry = lift_ds.entry()
        entry.set_id(f"mia_{self.entry_count:06d}")

        # Lexical unit
        lu   = lift_ds.lexical_unit()
        form = lift_ds.form()
        form.set_lang('mia')          # ISO 639-3 for Miami-Illinois
        form.set_text(item['headword'])
        lu.get_form().append(form)
        entry.set_lexical_unit(lu)

        # Pronunciation / IPA
        if item.get('ipa'):
            pron = lift_ds.pronunciation()
            pf   = lift_ds.form()
            pf.set_lang('mia-fonipa')
            pf.set_text(item['ipa'])
            pron.get_form().append(pf)
            entry.get_pronunciation().append(pron)

        # Sense with glosses
        sense = lift_ds.sense()
        sense.set_id(f"mia_{self.entry_count:06d}.s1")

        for lang, field in [('en', 'gloss_en'), ('fr', 'gloss_fr')]:
            if item.get(field):
                gloss = lift_ds.gloss()
                gloss.set_lang(lang)
                gloss.set_text(item[field])
                sense.get_gloss().append(gloss)

        # Example sentence
        if item.get('example'):
            ex   = lift_ds.example()
            exf  = lift_ds.form()
            exf.set_lang('mia')
            exf.set_text(item['example'])
            ex.get_form().append(exf)
            if item.get('trans'):
                tr  = lift_ds.translation()
                trf = lift_ds.form()
                trf.set_lang('en')
                trf.set_text(item['trans'])
                tr.get_form().append(trf)
                tr.set_type('Frame sentence')
                ex.get_translation().append(tr)
            sense.get_example().append(ex)

        # Source reference as field
        if item.get('source_ref'):
            fld = lift_ds.field()
            fld.set_type('source-ref')
            ff  = lift_ds.form()
            ff.set_lang('en')
            ff.set_text(item['source_ref'])
            fld.get_form().append(ff)
            entry.get_field().append(fld)

        entry.get_sense().append(sense)
        self.lift_root.get_entry().append(entry)
        self.entry_count += 1
        return item

    def close_spider(self, spider):
        out = f"ilad_miami_{self.entry_count}_entries.lift"
        with open(out, 'w', encoding='utf-8') as fh:
            self.lift_root.export(fh, 0)
        spider.logger.info(
            f"LIFT export: {self.entry_count} entries → {out}"
        )
        # Then straight into the pipeline:
        # lift-to-xliff.xsl → weblate_adapter.push_xliff()
Then the Weblate leg is just:
from tools.weblate_adapter import WeblateAdapter
from saxonche import PySaxonProcessor

# LIFT → XLIFF
proc = PySaxonProcessor(license=False)
xp   = proc.new_xslt30_processor()
xp.set_parameter('source-lang', proc.make_string_value('mia'))
xp.set_parameter('target-lang',  proc.make_string_value('en'))
exe  = xp.compile_stylesheet(stylesheet_file='xslt/lift-to-xliff.xsl')
xliff = exe.transform_to_string(source_file='ilad_miami_entries.lift')

with open('miami_illinois.xliff', 'w') as f:
    f.write(xliff)

# Push to Weblate — replaces all your manual copy-paste
wba = WeblateAdapter()
wba.push_xliff('myaamia-project', 'ilad-lexicon', 'en', 'miami_illinois.xliff')
That whole chain runs unattended and gets you from ILAD HTML to Weblate strings in one shot. The hand-scraping sessions you've already done — if even some of that is in a consistent format (spreadsheet, text file, partial LIFT) it's worth piping through the generateDS bindings to normalize it before it goes any further. Saves fixing inconsistencies later when the corpus is larger.
The Myaamia Center people would probably be genuinely interested in this tooling once it's on GitHub too. They've been doing serious digital infrastructure work for the revitalization effort.

Kickapoo — yes, and it's a fascinating data point in the Algonquian family tree.
The Kickapoo position is linguistically interesting
It sits closest to Sauk-Fox (Meskwaki) and Potawatomi in the Central Algonquian cluster, arguably closer than either is to Miami-Illinois. The four together form a really tight comparative set:
Proto-Algonquian
    └── Central Algonquian
            ├── Ojibwe-Potawatomi
            │       ├── Ojibwe dialect continuum
            │       └── Potawatomi
            └── Sac-Fox-Kickapoo
                    ├── Meskwaki (Sac-Fox)
                    ├── Kickapoo
                    └── [Miami-Illinois — slightly more distant
                         but close enough for cognate leverage]
What makes Kickapoo particularly valuable for your corpus
The diaspora situation is unique — there are Kickapoo communities in:
Kansas (Prairie Band adjacent)
Oklahoma (Oklahoma Kickapoo)
Texas/Mexico border (Kickapoo Traditional Tribe of Texas / Kickapoo in Coahuila)
The Mexican Kickapoo community has maintained the language with remarkable vitality partly because of relative isolation — their variety is arguably the most conservative phonologically. That's rare and extremely useful as a comparative anchor, same reason Meskwaki is valuable.
Known data sources
Paul Voorhis did substantial Kickapoo documentation in the 1970s-80s — some deposited, some still in manuscript form at Kansas university archives
AILLA has some Kickapoo deposits
SIL did work with Oklahoma Kickapoo — some of that may have LIFT-compatible exports already given SIL's toolchain
The Kickapoo Tribe in Kansas has had language revitalization programs that produced pedagogical materials — some publicly accessible
The regex/morphophonology angle
Kickapoo shares the Central Algonquian initial change system with Meskwaki and Potawatomi but has some unique reflexes of the PA consonant clusters — particularly the treatment of *šk and *šp sequences that pattern differently from Ojibwe. For your pan-Algonquian regex normalization layer, Kickapoo is actually a good stress test because:
# PA *eː → Kickapoo i: (vs Ojibwe ii, Meskwaki ee)
# PA *aː → Kickapoo a: (relatively stable, good anchor)
# PA *θ  → Kickapoo h (vs Meskwaki θ retention)
# Initial change: e- prefix on certain verb forms
#   Kickapoo marks it more consistently than some dialects

# Rough sketch of correspondence rules
PA_TO_KICKAPOO = [
    (r'(?<=[#])e',  'i'),     # initial change environment
    (r'šk',         'hk'),    # PA cluster reflex
    (r'šp',         'hp'),
    (r'θ',          'h'),     # theta > h
]
For the SQLite cognate schema
Adding Kickapoo to the language table with the Sac-Fox-Kickapoo subfamily tag means your Ollama model gets the tightest possible comparative signal for that subgroup — Meskwaki and Kickapoo are close enough that cognate pairs are dense and morpheme boundaries are highly parallel. That's good training data structure.
INSERT INTO language VALUES 
    ('kic', 'Algonquian', 'Sac-Fox-Kickapoo', 'voorhis-roman'),
    ('sac', 'Algonquian', 'Sac-Fox-Kickapoo', 'meskwaki-syllabary'),
    ('pot', 'Algonquian', 'Central',           'fiero-variant'),
    ('mia', 'Algonquian', 'Miami-Illinois',     'costa-roman');
The Mexico Kickapoo data in particular — if any of it surfaces through AILLA requests — would be genuinely novel training material. Most NLP work on Algonquian languages has never touched it.
Good instinct adding it to the family set. When the scraper infrastructure is running on ILAD, Kickapoo deposits are a natural next target.


