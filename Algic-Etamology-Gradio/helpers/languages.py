from languages import (
    get_language,
    get_iso639_3,
    get_languages_by_group,
)

"""
Algic Language Registry
=======================

Shared language metadata for Gradio, TMX, TTL, JSONL,
dictionary crawling, and audio provenance.

Canonical language codes use ISO 639-3 where available.
Project-specific variety codes are not ISO identifiers.
"""

from typing import TypedDict


class Variety(TypedDict, total=False):
    name: str
    country: str
    region: str
    wiktionary: str
    sources: list[str]


class Language(TypedDict, total=False):
    name: str
    group: str
    subfamily: str
    iso639_3: str
    glottocode: str
    wals: str
    wiktionary: str
    varieties: dict[str, Variety]
    aliases: list[str]
    features: dict[str, str]
    status: str


ALGIC_LANGUAGE_REGISTRY: dict[str, Language] = {

    # === PLAINS ===

    "bft": {
        "name": "Blackfoot",
        "group": "Plains",
        "subfamily": "Algonquian",
        "iso639_3": "bla",
        "glottocode": "siks1238",
        "wals": "bla",
    },

    "arp": {
        "name": "Arapaho",
        "group": "Plains",
        "subfamily": "Algonquian",
        "iso639_3": "arp",
        "glottocode": "arap1274",
        "wals": "ara",
    },

    "ats": {
        "name": "Gros Ventre",
        "group": "Plains",
        "subfamily": "Algonquian",
        "iso639_3": "ats",
        "glottocode": "gros1243",
        "wals": "ats",
    },

    "chy": {
        "name": "Cheyenne",
        "group": "Plains",
        "subfamily": "Algonquian",
        "iso639_3": "chy",
        "glottocode": "chey1247",
        "wals": "chy",
    },

    # === CENTRAL ===

    "men": {
        "name": "Menominee",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "mez",
        "glottocode": "meno1252",
        "wals": "men",
    },

    "cre": {
        "name": "Cree",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "cre",
        "glottocode": "cree1272",
        "wals": "cre",
    },

    "csw": {
        "name": "Swampy Cree",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "csw",
        "glottocode": "swam1239",
    },

    "crj": {
        "name": "Southern East Cree",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "crj",
        "glottocode": "sout2971",
    },

    "atj": {
        "name": "Atikamekw",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "atj",
        "glottocode": "atik1240",
        "wals": "atk",
    },

    "pot": {
        "name": "Potawatomi",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "pot",
        "glottocode": "pota1247",
        "wals": "pot",
    },

    "oji": {
        "name": "Ojibwe",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "oji",
        "glottocode": "ojib1240",
        "wals": "oji",
    },

    "otw": {
        "name": "Ottawa",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "otw",
        "glottocode": "otta1242",
        "wals": "ott",
    },

    "ciw": {
        "name": "Chippewa",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "ciw",
        "glottocode": "chip1241",
        "wals": "ojm",
        "features": {
            "77A": "Indirect only",
            "129A": "Different",
            "130A": "Different",
        },
    },

    "mia": {
        "name": "Miami-Illinois",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "mia",
        "glottocode": "miam1252",
        "wals": "mia",
    },

    "sac": {
        "name": "Meskwaki (Fox)",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "sac",
        "glottocode": "mesq1242",
        "wals": "fox",
    },

    # Kickapoo: one language, regional varieties
    "kic": {
        "name": "Kickapoo",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "kic",
        "glottocode": "kick1244",
        "wals": "kic",

        "varieties": {
            "kic-US": {
                "name": "Kickapoo (United States)",
                "country": "US",
                "sources": [],
            },
            "kic-MX": {
                "name": "Kickapoo (Mexico)",
                "name_native": "Kikapú",
                "country": "MX",
                "region": "Coahuila",
                "sources": [],
            },
        },
    },

    "sjw": {
        "name": "Shawnee",
        "group": "Central",
        "subfamily": "Algonquian",
        "iso639_3": "sjw",
        "glottocode": "shaw1249",
        "wals": "shw",
    },

    # === EASTERN ===

    "mic": {
        "name": "Mi'kmaq",
        "group": "Eastern",
        "subfamily": "Algonquian",
        "iso639_3": "mic",
        "glottocode": "mikm1235",
        "wals": "mic",
    },

    "abe": {
        "name": "Western Abenaki",
        "group": "Eastern",
        "subfamily": "Algonquian",
        "iso639_3": "abe",
        "glottocode": "west2629",
        "wals": "abw",
    },

    "aaq": {
        "name": "Eastern Abnaki",
        "group": "Eastern",
        "subfamily": "Algonquian",
        "iso639_3": "aaq",
        "glottocode": "east2542",
        "wals": "abe",
    },

    "mal": {
        "name": "Maliseet-Passamaquoddy",
        "group": "Eastern",
        "subfamily": "Algonquian",
        "iso639_3": "pqm",
        "glottocode": "mali1279",
    },

    "moo": {
        "name": "Mohegan-Pequot",
        "group": "Eastern",
        "subfamily": "Algonquian",
        "iso639_3": "xpq",
        "glottocode": "mohe1244",
    },

    "mua": {
        "name": "Munsee",
        "group": "Eastern",
        "subfamily": "Algonquian",
        "iso639_3": "umu",
        "glottocode": "muns1251",
        "wals": "del",
    },

    "unm": {
        "name": "Unami",
        "group": "Eastern",
        "subfamily": "Algonquian",
        "iso639_3": "unm",
        "glottocode": "unam1242",
        "wals": "del",
    },

    # === WESTERN OUTLIERS ===

    "yur": {
        "name": "Yurok",
        "group": "Western",
        "subfamily": "Ritwan",
        "iso639_3": "yur",
        "glottocode": "yuro1248",
        "wals": "yur",
    },

    "wiy": {
        "name": "Wiyot",
        "group": "Western",
        "subfamily": "Ritwan",
        "iso639_3": "wiy",
        "glottocode": "wiyo1248",
        "wals": "wiy",
    },

    # === REMNANT / HISTORICAL ===

    "bue": {
        "name": "Beothuk",
        "group": "Remnant",
        "subfamily": "Algonquian",
        "iso639_3": "bue",
        "glottocode": "beot1247",
        "status": "Extinct",
    },

    "etc": {
        "name": "Etchemin",
        "group": "Remnant",
        "subfamily": "Algonquian",
        "iso639_3": "etc",
        "glottocode": "etc2543",
        "status": "Historical",
    },

    "xlo": {
        "name": "Loup A",
        "group": "Remnant",
        "subfamily": "Algonquian",
        "iso639_3": "xlo",
        "glottocode": "loup1244",
        "status": "Historical",
    },

    "xlb": {
        "name": "Loup B",
        "group": "Remnant",
        "subfamily": "Algonquian",
        "iso639_3": "xlb",
        "glottocode": "loup1245",
        "status": "Historical",
    },

    "crr": {
        "name": "Lumbee",
        "group": "Remnant",
        "subfamily": "Algonquian",
        "iso639_3": "lmz",
        "glottocode": "lumI1234",
        "status": "Historical / disputed classification",
    },

    "pim": {
        "name": "Powhatan",
        "group": "Remnant",
        "subfamily": "Algonquian",
        "iso639_3": "pim",
        "glottocode": "powh1243",
        "status": "Historical",
    },

    "qyp": {
        "name": "Quiripi",
        "group": "Remnant",
        "subfamily": "Algonquian",
        "iso639_3": "qyp",
        "glottocode": "quir1242",
        "status": "Historical",
    },

    # === ANCESTRAL ===

    "alg-pro": {
        "name": "Proto-Algonquian",
        "group": "Ancestral",
        "subfamily": "Proto",
        "iso639_3": "alg",
        "wiktionary": "alg-pro",
        "glottocode": "algo1256",
        "wals": "pal",
        "aliases": ["alg-x-proto"],
        "status": "Reconstructed",
    },
}


# === GRADIO HELPERS ===

def language_choices(group: str | None = None) -> list[tuple[str, str]]:
    """Return (display_name, code) choices for a Gradio dropdown."""
    choices = []

    for code, lang in ALGIC_LANGUAGE_REGISTRY.items():
        if group and lang["group"] != group:
            continue

        choices.append((f'{lang["name"]} ({code})', code))

    return choices


def variety_choices(language_code: str) -> list[tuple[str, str]]:
    """Return varieties for a selected language."""
    lang = ALGIC_LANGUAGE_REGISTRY.get(language_code, {})

    return [
        (variety["name"], code)
        for code, variety in lang.get("varieties", {}).items()
    ]


def get_language(code: str) -> Language:
    """Resolve canonical language code or legacy alias."""
    code = code.lower()

    if code in ALGIC_LANGUAGE_REGISTRY:
        return ALGIC_LANGUAGE_REGISTRY[code]

    for language in ALGIC_LANGUAGE_REGISTRY.values():
        if code in language.get("aliases", []):
            return language

        if code == language.get("iso639_3"):
            return language

    raise KeyError(f"Unknown language code: {code}")


def get_variety(code: str) -> Variety:
    """Resolve a project variety code such as kic-MX."""
    language_code = code.split("-", 1)[0]

    language = get_language(language_code)

    try:
        return language["varieties"][code]
    except KeyError:
        raise KeyError(f"Unknown language variety: {code}") from None


def get_iso639_3(code: str) -> str:
    """Return the ISO 639-3 code."""
    return get_language(code)["iso639_3"]


def get_languages_by_group(group: str) -> dict[str, Language]:
    """Filter registry by language group."""
    return {
        code: lang
        for code, lang in ALGIC_LANGUAGE_REGISTRY.items()
        if lang["group"].lower() == group.lower()
    }


def validate_registry() -> list[str]:
    """Basic registry validation."""
    errors = []

    for code, lang in ALGIC_LANGUAGE_REGISTRY.items():
        iso = lang.get("iso639_3")

        if not iso or len(iso) != 3:
            errors.append(f"{code}: invalid ISO 639-3: {iso}")

        for variety_code in lang.get("varieties", {}):
            if not variety_code.startswith(f"{code}-"):
                errors.append(
                    f"{code}: invalid variety code {variety_code}"
                )

    return errors
