# helpers/io_plugin.py
import os
import sqlite3
import uuid
import sys
from pathlib import Path
from transmog import TransmogEngine
import visualization

XSLT_REGISTRY = {
    "xdxf2tmx": "xdxf2tmx.xsl", "xdxf2xliff": "xdxf2xliff.xsl",
    "xliff2tmx": "xliff2tmx.xsl", "xliff2xdxf": "xliff2xdxf.xsl",
    "xliff2lift": "xliff-to-lift.xsl", "lemon2lift": "Lemon2LIFT.xslt",
    "lift2lemon": "LIFT2lemon.xslt", "eaf2lift": "eaf-to-lift.xsl",
    "eaf2tei": "eaf-to-tei.xsl", "eaf2tmx": "eaf-to-tmx.xsl",
    "eaf2xliff": "eaf-to-xliff.xsl", "flex2xdxf": "flex2xdxf.xsl",
    "lemon2tei": "lemon2tei.xsl", "lift2tmx": "lift-to-tmx.xsl",
    "lift2xliff": "lift-to-xliff.xsl", "olif2xdxf": "olif2xdxf.xsl",
    "tmx2xdxf": "tmx2xdxf.xsl", "tmx2eaf": "tmx-to-eaf.xsl",
    "tmx2lift": "tmx-to-lift.xsl", "tmx2xliff": "tmx-to-xliff.xsl"
}

class LinguisticIOPlugin:
    def __init__(self, db_path: str, xslt_dir: str):
        self.db_path = db_path
        self.xslt_dir = xslt_dir

    def run_xslt_transform(self, mapping_key: str, xml_bytes: bytes, src_lang: str) -> bytes:
        if mapping_key not in XSLT_REGISTRY:
            raise ValueError(f"Mapping signature unlisted: {mapping_key}")
            
        sheet_path = Path(self.xslt_dir) / XSLT_REGISTRY[mapping_key]
        from saxonche import PySaxonProcessor
        
        with PySaxonProcessor(license=False) as proc:
            xslt = proc.new_xslt30_processor()
            exe = xslt.compile_stylesheet(stylesheet_file=str(sheet_path))
            exe.set_parameter("source-lang", proc.make_string_value(src_lang))
            
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tf:
                tf.write(xml_bytes)
                tf_name = tf.name
            try:
                result = exe.transform_to_string(source_file=tf_name)
            finally:
                os.unlink(tf_name)
            return result.encode("utf-8") if isinstance(result, str) else result

    def process_universal_import(self, format_type: str, file_bytes: bytes, src_lang: str) -> dict:
        fmt = format_type.lower().strip()
        records = []

        if fmt == "extended-tmx" or (fmt == "tmx" and b"prop" in file_bytes):
            records = TransmogEngine.parse_extended_tmx(file_bytes)
        elif fmt == "xdxf":
            records = TransmogEngine.parse_xdxf(file_bytes)
        elif fmt in ("ttl", "lemon-ttl"):
            records = TransmogEngine.parse_ontolex_lemon_ttl(file_bytes)
        elif fmt in XSLT_REGISTRY:
            transformed_xml = self.run_xslt_transform(fmt, file_bytes, src_lang)
            if "lift" in fmt:
                return {"status": "transformed", "output_format": "lift", "preview": transformed_xml[:300].decode(errors="ignore")}
            return {"status": "xslt transformation applied"}
        else:
            return {"error": f"No pipeline registered for format signature: {format_type}"}

        inserted = 0
        with sqlite3.connect(self.db_path) as conn:
            for r in records:
                eid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{src_lang}:{r['form']}"))
                cursor = conn.execute("SELECT 1 FROM entries WHERE id=?", (eid,))
                if not cursor.fetchone():
                    conn.execute("""
                        INSERT INTO entries (id, lang, form, gloss_en, proto_form, source_url, source_type, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 0.8)
                    """, (eid, src_lang, r['form'], r['gloss_en'], r['proto_form'], r['source_url'], r['source_type']))
                    inserted += 1
            conn.commit()

        if inserted > 0:
            visualization.update_and_render_cache()

        return {"total_seen": len(records), "new_inserted": inserted}
