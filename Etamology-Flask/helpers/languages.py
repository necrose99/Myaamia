# languages.py

ALGIC_LANGUAGE_REGISTRY = {
    # === PLAINS ===
    "bft": {
        "name": "Blackfoot", "group": "Plains", "subfamily": "Algonquian",
        "glottocode": "siks1238", "iso": "bla", "wals": "blk",
        "features": {"77A": "No grammatical evidentials", "129A": "Different", "130A": "Different"}
    },
    "arp": {
        "name": "Arapaho", "group": "Plains", "subfamily": "Algonquian",
        "glottocode": "arap1274", "iso": "arp", "wals": "ara",
        "features": {"77A": "No grammatical evidentials", "129A": "Identical", "130A": "Different"}
    },
    "ats": {"name": "Gros Ventre", "group": "Plains", "subfamily": "Algonquian", "glottocode": "gros1243", "iso": "ats", "wals": "ats"},
    "chy": {"name": "Cheyenne", "group": "Plains", "subfamily": "Algonquian", "glottocode": "chey1247", "iso": "chy", "wals": "chy"},

    # === CENTRAL ===
    "men": {"name": "Menominee", "group": "Central", "subfamily": "Algonquian", "glottocode": "meno1252", "iso": "mez", "wals": "men"},
    "cre": {"name": "Cree", "group": "Central", "subfamily": "Algonquian", "glottocode": "cree1272", "iso": "cre", "wals": "cre"},
    "csw": {"name": "Swampy Cree", "group": "Central", "subfamily": "Algonquian", "glottocode": "swam1239", "iso": "csw", "wals": "crs"},
    "crj": {"name": "Southern East Cree", "group": "Central", "subfamily": "Algonquian", "glottocode": "sout2971", "iso": "crj", "wals": "cre"},
    "atj": {"name": "Atikamekw", "group": "Central", "subfamily": "Algonquian", "glottocode": "atik1240", "iso": "atj", "wals": "atk"},
    "pot": {"name": "Potawatomi", "group": "Central", "subfamily": "Algonquian", "glottocode": "pota1247", "iso": "pot", "wals": "pot"},
    "oji": {"name": "Ojibwe", "group": "Central", "subfamily": "Algonquian", "glottocode": "ojib1240", "iso": "oji", "wals": "oji"},
    "otw": {"name": "Ottawa", "group": "Central", "subfamily": "Algonquian", "glottocode": "otta1242", "iso": "otw", "wals": "ott"},
    "ciw": {
        "name": "Chippewa", "group": "Central", "subfamily": "Algonquian",
        "glottocode": "chip1241", "iso": "ciw", "wals": "oJM",
        "features": {"77A": "Indirect only", "129A": "Different", "130A": "Different"}
    },
    "mia": {"name": "Miami-Illinois", "group": "Central", "subfamily": "Algonquian", "glottocode": "miam1252", "iso": "mia", "wals": "mia"},
    "sac": {"name": "Meskwaki (Fox)", "group": "Central", "subfamily": "Algonquian", "glottocode": "mesq1242", "iso": "sac", "wals": "fox"},
    "kic": {"name": "Kickapoo", "group": "Central", "subfamily": "Algonquian", "glottocode": "kick1244", "iso": "kic", "wals": "kic"},
    "sjw": {"name": "Shawnee", "group": "Central", "subfamily": "Algonquian", "glottocode": "shaw1249", "iso": "sjw", "wals": "shw"},

    # === EASTERN ===
    "mic": {"name": "Mi'kmaq", "group": "Eastern", "subfamily": "Algonquian", "glottocode": "mikm1235", "iso": "mic", "wals": "mic"},
    "abe": {"name": "Western Abenaki", "group": "Eastern", "subfamily": "Algonquian", "glottocode": "west2629", "iso": "abe", "wals": "abw"},
    "aaq": {"name": "Eastern Abnaki", "group": "Eastern", "subfamily": "Algonquian", "glottocode": "east2542", "iso": "aaq", "wals": "abe"},
    "mal": {"name": "Maliseet-Passamaquoddy", "group": "Eastern", "subfamily": "Algonquian", "glottocode": "mali1279", "iso": "mal", "wals": "mal"},
    "moo": {"name": "Mohegan-Pequot", "group": "Eastern", "subfamily": "Algonquian", "glottocode": "mohe1244", "iso": "moo", "wals": "moh"},
    "mua": {"name": "Munsee", "group": "Eastern", "subfamily": "Algonquian", "glottocode": "muns1251", "iso": "mua", "wals": "del"},
    "unm": {"name": "Unami", "group": "Eastern", "subfamily": "Algonquian", "glottocode": "unam1242", "iso": "unm", "wals": "del"},

    # === WESTERN OUTLIERS ===
    "yur": {"name": "Yurok", "group": "Western", "subfamily": "Ritwan (CA)", "glottocode": "yuro1248", "iso": "yur", "wals": "yur"},
    "wiy": {"name": "Wiyot", "group": "Western", "subfamily": "Ritwan (CA)", "glottocode": "wiyo1248", "iso": "wiy", "wals": "wiy"},

    # === REMNANT / UNATTESTED ===
    "bue": {"name": "Beothuk", "group": "Remnant", "subfamily": "Algonquian", "glottocode": "beot1247", "iso": "bue", "wals": "beo"},
    "etc": {"name": "Etchemin", "group": "Remnant", "subfamily": "Algonquian", "glottocode": "etc2543", "iso": "etc", "wals": "etc"},
    "xlo": {"name": "Loup A", "group": "Remnant", "subfamily": "Algonquian", "glottocode": "loup1244", "iso": "xlo", "wals": "lpa"},
    "xlb": {"name": "Loup B", "group": "Remnant", "subfamily": "Algonquian", "glottocode": "loup1245", "iso": "xlb", "wals": "lpb"},
    "crr": {"name": "Lumbee", "group": "Remnant", "subfamily": "Algonquian", "glottocode": "lumI1234", "iso": "crr", "wals": "lum"},
    "pim": {"name": "Powhatan", "group": "Remnant", "subfamily": "Algonquian", "glottocode": "powh1243", "iso": "pim", "wals": "pow"},
    "qyp": {"name": "Quiripi", "group": "Remnant", "subfamily": "Algonquian", "glottocode": "quir1242", "iso": "qyp", "wals": "qyp"},
    
    # === ANCESTRAL ===
    "alg-x-proto": {"name": "Proto-Algonquian", "group": "Ancestral", "subfamily": "Proto", "glottocode": "algo1256", "iso": "alg", "wals": "pal"}
}
