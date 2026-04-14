This is the blueprint for an "off-the-rack" linguistic data pipeline. By combining the archival stability of **LIFT**, the semantic richness of **OntoLex-Lemon**, and the high-performance retrieval of **sqlite-rag** with **zstd** compression, you create a system that is both internationally compliant and AI-ready.
Below is the pasteable Markdown for your project or skill-set documentation.
# Skill: Bidirectional Linguistic Engineering (LIFT & OntoLex-Lemon)
## 🎯 Overview
A standardized framework for converting, refining, and searching large-scale linguistic datasets (specifically Algic/Miami-Illinois). This approach eliminates "MacGyvered" custom formats by using international standards (**ISO 639-3**, **SIL LIFT**, **W3C OntoLex**) for agentic pipelines, etymological research, and RAG-enabled language models.
## 🛠 The Tech Stack
 * **Source Format:** LIFT (Lexical Interchange Format) — *The Archival Standard.*
 * **Graph Format:** OntoLex-Lemon — *The Linked Data/AI Standard.*
 * **Processor:** saxonche (Saxon-HE 12+) — *XSLT 3.0 for XML-to-JSON/RDF.*
 * **Storage:** SQLite + sqlite-rag + zstd — *For high-performance semantic search.*
 * **Validation:** XSD synthesized from LIFT 0.13.
## 🔄 Round-Trip XSLT Architecture
### 1. Inbound: LIFT ➔ OntoLex-Lemon
Converts hierarchical XML into a flat, relational, or graph-based structure for RAG consumption.
 * **Logic:** Maps lexical-unit to ontolex:canonicalForm and trait elements to lemon:property.
 * **Etymology Bonus:** Extracts <etymology> and <relation> tags to build cognate linkage graphs.
 * **Application:** Feeding vector databases for semantic search (Natural Language Search).
### 2. Outbound: OntoLex-Lemon ➔ LIFT
Restores graph-based improvements back into a compliant XML format for archival tools (FLEx, Lexique Pro).
 * **Logic:** Reconstructs the SIL-compliant XML structure from RDF triples.
 * **Validation:** Uses <xs:include schemaLocation=".../lift.xsd"/> via Saxon to ensure "off-the-rack" compatibility.
## 📦 Data Pipeline for Agentic RAG
To handle "large reams of raw linguistics data" without being "screwed" by performance limits, follow this pipeline:
 1. **Normalization:** Validate source LIFT against the synthesized XSD.
 2. **Transformation:** Use XSLT 3.0 to output **JSON Lines** containing lemma, definition, and Algic traits (animacy, transitivity).
 3. **Compression:** Use **zstd** to compress raw XML/JSON blobs before SQL storage to save space on massive datasets.
 4. **Vectorization:** Embed the sense definitions using sqlite-rag.
 5. **Hybrid Querying:**
   * **SQL:** Find all *Transitive Animate (TA)* verbs in Miami-Illinois.
   * **Vector:** Find words semantically related to "walking along the river."
   * **Etymology:** Retrieve Proto-Algic roots for the result set.
## 🏛 Algic Use Case Application
For languages like **Miami-Illinois**, **Sauk**, or **Fox (Meskwaki)**:
 * **Constraint:** These languages are morphologically heavy (polysynthetic).
 * **Solution:** Use the LIFT trait system to store transitivity and command forms.
 * **Agentic Advantage:** An LLM can "read" the JSONB metadata produced by this skill to understand *how* to conjugate a verb before generating a response, rather than hallucinating grammar.
## 🔗 Resources
 * **LIFT XSD:** Official SIL Spec
 * **LIFT2Lemon:** Transformation Logic
 * **Lemon2LIFT:** Inversion Logic
### 💡 Why this matters
By not reinventing the wheel, we ensure that Myaamia data—and any Algic cousin data—is ready for the next 20 years of AI development while remaining perfectly readable by the linguistic tools of the last 20 years. **No McGuyvering required.**
Would you like a Python orchestration script to automate the **zstd** compression and **sqlite-rag** indexing for these LIFT files?
