#!/usr/bin/env python3
"""
crawl_wiwk_update.py

Crawl Potawatomi entries from:
    https://wiwkwebthegen.com/dictionary

Individual entries:
    https://wiwkwebthegen.com/dictionary-word/<headword>

Output:
    potawatomi_full.tmx

Language pair:
    pot -> en

The crawler is intentionally link-based rather than ID-based because
Wiwkwébthëgen uses dictionary-word/<headword> URLs.

Features:
    - Resumable crawling
    - Persistent JSON state
    - Dictionary pagination discovery
    - Actual headword URL discovery
    - UTF-8 / Potawatomi diacritics
    - Duplicate protection
    - Incremental TMX writing
    - Audio URL capture when available
    - Source URL capture
    - Morpheme detection
    - Optional word-list metadata
    - Polite request delay
    - Retry handling
"""

import os
import re
import json
import time
import argparse
import logging
from urllib.parse import urljoin, urlparse, unquote

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://wiwkwebthegen.com"

DICTIONARY_URL = f"{BASE_URL}/dictionary"

TMX_FILE = "potawatomi_full.tmx"
WORK_JSON = "./tmp/wiwk_work.json"

SOURCE_LANG = "pot"
TARGET_LANG = "en"

DEFAULT_DELAY = 0.5
DEFAULT_TIMEOUT = 20
DEFAULT_RETRIES = 3

USER_AGENT = (
    "Mozilla/5.0 (compatible; crawl_wiwk_update/1.0; "
    "+https://github.com/necrose99/Myaamia)"
)

WORD_PATH_PREFIX = "/dictionary-word/"

# Only accept dictionary-word links from the target site.
WORD_URL_RE = re.compile(
    r"^/dictionary-word/.+",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

log = logging.getLogger("wiwk")


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def create_session():
    session = requests.Session()

    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.8",
        }
    )

    return session


def get_page(session, url, timeout=DEFAULT_TIMEOUT, retries=DEFAULT_RETRIES):
    """
    Fetch a page with simple retry/backoff handling.
    """

    last_error = None

    for attempt in range(1, retries + 1):

        try:
            response = session.get(
                url,
                timeout=timeout,
                allow_redirects=True,
            )

            if response.status_code == 200:
                return response

            if response.status_code in (429, 500, 502, 503, 504):
                log.warning(
                    "HTTP %s for %s; retry %d/%d",
                    response.status_code,
                    url,
                    attempt,
                    retries,
                )

                time.sleep(attempt * 2)
                continue

            log.warning(
                "HTTP %s for %s",
                response.status_code,
                url,
            )

            return None

        except requests.RequestException as exc:
            last_error = exc

            log.warning(
                "Request error for %s: %s; retry %d/%d",
                url,
                exc,
                attempt,
                retries,
            )

            time.sleep(attempt * 2)

    log.error(
        "Failed after %d attempts: %s",
        retries,
        last_error,
    )

    return None


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def default_state():
    return {
        "processed_urls": {},
        "discovered_urls": {},
        "scanned_pages": {},
        "last_run": None,
    }


def load_state():
    if not os.path.exists(WORK_JSON):
        return default_state()

    try:
        with open(WORK_JSON, "r", encoding="utf-8") as fh:
            state = json.load(fh)

        # Upgrade older/incomplete state files gracefully.
        for key, value in default_state().items():
            state.setdefault(key, value)

        return state

    except (OSError, json.JSONDecodeError) as exc:
        log.warning(
            "Could not load state file %s: %s",
            WORK_JSON,
            exc,
        )

        return default_state()


def save_state(state):
    directory = os.path.dirname(WORK_JSON)

    if directory:
        os.makedirs(directory, exist_ok=True)

    temp_file = WORK_JSON + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as fh:
        json.dump(
            state,
            fh,
            indent=2,
            ensure_ascii=False,
        )

    os.replace(temp_file, WORK_JSON)


# ---------------------------------------------------------------------------
# TMX
# ---------------------------------------------------------------------------

def create_tmx():
    """
    Create a new TMX document.
    """

    root = ET.Element(
        "tmx",
        {
            "version": "1.4",
        },
    )

    header = ET.SubElement(
        root,
        "header",
        {
            "creationtool": "crawl_wiwk_update.py",
            "creationtoolversion": "1.0",
            "segtype": "sentence",
            "adminlang": "en",
            "srclang": SOURCE_LANG,
            "datatype": "PlainText",
        },
    )

    body = ET.SubElement(root, "body")

    return ET.ElementTree(root)


def ensure_tmx(file_path):
    if os.path.exists(file_path):
        try:
            return ET.parse(file_path)

        except ET.ParseError as exc:
            raise RuntimeError(
                f"Existing TMX file is invalid: {file_path}"
            ) from exc

    tree = create_tmx()

    tree.write(
        file_path,
        encoding="utf-8",
        xml_declaration=True,
    )

    return tree


def existing_tuids(tree):
    """
    Build a duplicate set from existing TMX records.

    New records use a stable ID based on the normalized source URL.
    """

    result = set()

    root = tree.getroot()

    for tu in root.findall(".//tu"):

        tuid = tu.get("tuid")

        if tuid:
            result.add(tuid)

    return result


def stable_tuid(url):
    """
    Generate a deterministic TMX ID from the dictionary URL.

    Example:
        https://wiwkwebthegen.com/dictionary-word/angodogaw%C3%A9

    becomes:
        angodogawé
    """

    parsed = urlparse(url)

    path = parsed.path.rstrip("/")

    if path.lower().startswith(WORD_PATH_PREFIX.rstrip("/").lower()):
        value = path[len(WORD_PATH_PREFIX.rstrip("/")):]
    else:
        value = path.rsplit("/", 1)[-1]

    value = unquote(value)

    value = re.sub(r"\s+", " ", value).strip()

    return value


def append_tu(tree, record):
    """
    Add one translation unit to the TMX tree.
    """

    body = tree.getroot().find("body")

    if body is None:
        body = ET.SubElement(tree.getroot(), "body")

    tu = ET.SubElement(
        body,
        "tu",
        {
            "tuid": record["tuid"],
        },
    )

    # -----------------------------------------------------------------------
    # Metadata
    # -----------------------------------------------------------------------

    prop = ET.SubElement(
        tu,
        "prop",
        {
            "type": "source",
        },
    )

    prop.text = "Wiwkwébthëgen"

    prop = ET.SubElement(
        tu,
        "prop",
        {
            "type": "source_url",
        },
    )

    prop.text = record["url"]

    prop = ET.SubElement(
        tu,
        "prop",
        {
            "type": "language",
        },
    )

    prop.text = "Potawatomi"

    if record.get("is_morpheme"):
        prop = ET.SubElement(
            tu,
            "prop",
            {
                "type": "entry_type",
            },
        )

        prop.text = "morpheme"

    if record.get("audio_urls"):
        for audio_url in record["audio_urls"]:
            prop = ET.SubElement(
                tu,
                "prop",
                {
                    "type": "audio_url",
                },
            )

            prop.text = audio_url

    for word_list in record.get("word_lists", []):
        prop = ET.SubElement(
            tu,
            "prop",
            {
                "type": "word_list",
            },
        )

        prop.text = word_list

    # -----------------------------------------------------------------------
    # Potawatomi
    # -----------------------------------------------------------------------

    tuv_pot = ET.SubElement(
        tu,
        "tuv",
        {
            "xml:lang": SOURCE_LANG,
        },
    )

    ET.SubElement(
        tuv_pot,
        "seg",
    ).text = record["pot"]

    # -----------------------------------------------------------------------
    # English
    # -----------------------------------------------------------------------

    tuv_en = ET.SubElement(
        tu,
        "tuv",
        {
            "xml:lang": TARGET_LANG,
        },
    )

    ET.SubElement(
        tuv_en,
        "seg",
    ).text = record["en"]


def write_tmx(tree):
    """
    Rewrite TMX atomically.
    """

    temp_file = TMX_FILE + ".tmp"

    tree.write(
        temp_file,
        encoding="utf-8",
        xml_declaration=True,
    )

    os.replace(temp_file, TMX_FILE)


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def clean_text(element):
    if not element:
        return ""

    text = element.get_text(
        " ",
        strip=True,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def absolute_url(url):
    return urljoin(
        BASE_URL,
        url,
    )


def is_word_url(url):
    parsed = urlparse(url)

    if parsed.netloc:
        # Only accept the target host.
        if parsed.netloc.lower() != urlparse(BASE_URL).netloc.lower():
            return False

    return bool(
        WORD_URL_RE.match(
            parsed.path
        )
    )


# ---------------------------------------------------------------------------
# Dictionary index parsing
# ---------------------------------------------------------------------------

def extract_word_links(html, page_url):
    """
    Extract all /dictionary-word/... links from a dictionary browse page.
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    links = {}

    for anchor in soup.find_all("a", href=True):

        href = anchor.get("href", "").strip()

        if not href:
            continue

        full_url = absolute_url(href)

        if not is_word_url(full_url):
            continue

        # Remove query/fragment.
        parsed = urlparse(full_url)

        clean_url = (
            f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        )

        title = clean_text(anchor)

        links[clean_url] = {
            "url": clean_url,
            "link_text": title,
        }

    return links


def extract_next_page(html, page_url):
    """
    Find the Drupal-style "next" dictionary page.

    Falls back to ?page=N when necessary.
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # First try semantic pager links.
    for anchor in soup.find_all("a", href=True):

        text = clean_text(anchor).lower()

        if text in (
            "next",
            "next ›",
            "next »",
            "›",
            "»",
        ):
            return absolute_url(
                anchor["href"]
            )

    # Try common rel=next.
    anchor = soup.find(
        "a",
        rel=lambda value: (
            value
            and (
                "next" in value
                if isinstance(value, str)
                else "next" in value
            )
        ),
    )

    if anchor and anchor.get("href"):
        return absolute_url(anchor["href"])

    # Finally, increment ?page=N.
    parsed = urlparse(page_url)

    query_match = re.search(
        r"(?:^|&)page=(\d+)",
        parsed.query,
    )

    if query_match:
        current_page = int(query_match.group(1))
        next_page = current_page + 1

    else:
        # /dictionary is page 0.
        next_page = 1

    # Avoid blindly generating pages if this isn't a dictionary URL.
    if parsed.path.rstrip("/") != "/dictionary":
        return None

    return (
        f"{BASE_URL}/dictionary"
        f"?page={next_page}"
    )


# ---------------------------------------------------------------------------
# Entry parsing
# ---------------------------------------------------------------------------

def extract_audio_urls(soup, page_url):
    urls = []

    # Standard HTML5 audio.
    for audio in soup.find_all("audio"):

        src = audio.get("src")

        if src:
            urls.append(
                absolute_url(src)
            )

        for source in audio.find_all(
            "source",
            src=True,
        ):
            urls.append(
                absolute_url(
                    source["src"]
                )
            )

    # Occasionally audio may be represented directly by links.
    for anchor in soup.find_all("a", href=True):

        href = anchor["href"]

        if re.search(
            r"\.(mp3|wav|ogg|m4a|aac)(?:\?|$)",
            href,
            re.IGNORECASE,
        ):
            urls.append(
                absolute_url(href)
            )

    # Preserve order while removing duplicates.
    return list(
        dict.fromkeys(urls)
    )


def extract_word_lists(soup):
    """
    Try to capture dictionary taxonomy/word-list information.

    This is intentionally conservative because the site may change its
    Drupal markup.
    """

    results = []

    # Common Drupal taxonomy links.
    for anchor in soup.find_all("a", href=True):

        href = anchor["href"]

        text = clean_text(anchor)

        if not text:
            continue

        if (
            "word-list" in href.lower()
            or "word_list" in href.lower()
            or "/taxonomy/" in href.lower()
        ):
            results.append(text)

    return list(
        dict.fromkeys(results)
    )


def parse_entry(html, url):
    """
    Parse an individual dictionary-word page.
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # -----------------------------------------------------------------------
    # Headword
    # -----------------------------------------------------------------------

    headword = ""

    # Current site has the word in H1.
    for selector in (
        "h1",
        ".entry-headword",
        ".headword",
        ".field--name-title",
    ):

        elem = soup.select_one(selector)

        if elem:
            headword = clean_text(elem)
            break

    # -----------------------------------------------------------------------
    # English gloss / definition
    # -----------------------------------------------------------------------

    english = ""

    for selector in (
        ".definition",
        ".gloss",
        ".translation",
        ".field--name-field-definition",
        ".field--name-field-translation",
    ):

        elem = soup.select_one(selector)

        if elem:
            english = clean_text(elem)
            break

    # Current Wiwkwébthëgen pages are very simple. If the semantic
    # selectors above don't work, inspect the page's visible text.

    if headword and not english:

        # Remove the headword from obvious page structure and locate
        # nearby text nodes.
        h1 = soup.find("h1")

        if h1:
            candidates = []

            for node in h1.find_all_next(
                string=True
            ):

                text = re.sub(
                    r"\s+",
                    " ",
                    str(node),
                ).strip()

                if not text:
                    continue

                if text == headword:
                    continue

                if text.lower() in (
                    "recording(s)",
                    "recording",
                    "language:",
                ):
                    continue

                # Skip site footer.
                if text.startswith("©"):
                    continue

                candidates.append(text)

            if candidates:
                english = candidates[0]

    # -----------------------------------------------------------------------
    # Validate
    # -----------------------------------------------------------------------

    if not headword or not english:
        return None

    # -----------------------------------------------------------------------
    # Metadata
    # -----------------------------------------------------------------------

    audio_urls = extract_audio_urls(
        soup,
        url,
    )

    word_lists = extract_word_lists(
        soup
    )

    # -----------------------------------------------------------------------
    # Morpheme detection
    # -----------------------------------------------------------------------

    is_morpheme = (
        headword.startswith("-")
        or headword.endswith("-")
    )

    # -----------------------------------------------------------------------
    # Stable ID
    # -----------------------------------------------------------------------

    tuid = stable_tuid(url)

    return {
        "tuid": tuid,
        "url": url,
        "pot": headword,
        "en": english,
        "audio_urls": audio_urls,
        "word_lists": word_lists,
        "is_morpheme": is_morpheme,
    }


# ---------------------------------------------------------------------------
# Dictionary crawl
# ---------------------------------------------------------------------------

def discover_dictionary(
    session,
    state,
    delay=DEFAULT_DELAY,
    max_pages=None,
):
    """
    Walk the dictionary pagination and discover individual word URLs.
    """

    discovered = state["discovered_urls"]

    page_url = DICTIONARY_URL

    page_number = 0

    while page_url:

        if max_pages is not None and page_number >= max_pages:
            log.info(
                "Reached max-pages limit: %d",
                max_pages,
            )
            break

        # Normalize.
        page_url = page_url.rstrip("&? ")

        if page_url in state["scanned_pages"]:
            log.info(
                "Already scanned dictionary page: %s",
                page_url,
            )

            # We normally don't need to continue through an already-scanned
            # chain because the next URL should already have been stored.
            break

        page_number += 1

        log.info(
            "Scanning dictionary page %d: %s",
            page_number,
            page_url,
        )

        response = get_page(session, page_url)

        if response is None:
            log.error(
                "Stopping pagination at: %s",
                page_url,
            )
            break

        links = extract_word_links(
            response.text,
            page_url,
        )

        log.info(
            "Page %d: found %d dictionary-word links",
            page_number,
            len(links),
        )

        for url, metadata in links.items():

            if url not in discovered:
                discovered[url] = metadata

        state["scanned_pages"][page_url] = {
            "page_number": page_number,
            "found": len(links),
            "timestamp": time.time(),
        }

        save_state(state)

        next_url = extract_next_page(
            response.text,
            page_url,
        )

        if not next_url:
            log.info(
                "No next page found."
            )
            break

        if next_url == page_url:
            log.warning(
                "Next page equals current page; stopping."
            )
            break

        # Guard against accidentally looping through a malformed pager.
        if next_url in state["scanned_pages"]:
            log.info(
                "Next page already scanned: %s",
                next_url,
            )
            break

        page_url = next_url

        time.sleep(delay)

    return discovered


# ---------------------------------------------------------------------------
# Entry crawl
# ---------------------------------------------------------------------------

def crawl_entries(
    session,
    state,
    tree,
    delay=DEFAULT_DELAY,
):
    discovered = state["discovered_urls"]
    processed = state["processed_urls"]

    existing_ids = existing_tuids(tree)

    pending = [
        url
        for url in discovered
        if url not in processed
    ]

    log.info(
        "Discovered URLs: %d",
        len(discovered),
    )

    log.info(
        "Already processed: %d",
        len(processed),
    )

    log.info(
        "Pending entries: %d",
        len(pending),
    )

    new_count = 0
    failed_count = 0

    for number, url in enumerate(
        pending,
        start=1,
    ):

        log.info(
            "[%d/%d] Fetching %s",
            number,
            len(pending),
            url,
        )

        response = get_page(
            session,
            url,
        )

        if response is None:

            processed[url] = {
                "exists": False,
                "error": "request_failed",
                "timestamp": time.time(),
            }

            failed_count += 1

            save_state(state)

            time.sleep(delay)

            continue

        record = parse_entry(
            response.text,
            url,
        )

        if record is None:

            log.warning(
                "Could not parse entry: %s",
                url,
            )

            processed[url] = {
                "exists": True,
                "parsed": False,
                "timestamp": time.time(),
            }

            failed_count += 1

            save_state(state)

            time.sleep(delay)

            continue

        # ---------------------------------------------------------------
        # Duplicate protection
        # ---------------------------------------------------------------

        if record["tuid"] in existing_ids:

            log.info(
                "[SKIP] Existing TMX entry: %s",
                record["pot"],
            )

            processed[url] = {
                "exists": True,
                "parsed": True,
                "duplicate": True,
                "tuid": record["tuid"],
                "pot": record["pot"],
                "en": record["en"],
                "timestamp": time.time(),
            }

            save_state(state)

            time.sleep(delay)

            continue

        # ---------------------------------------------------------------
        # Append to TMX
        # ---------------------------------------------------------------

        append_tu(
            tree,
            record,
        )

        existing_ids.add(
            record["tuid"]
        )

        processed[url] = {
            "exists": True,
            "parsed": True,
            "tuid": record["tuid"],
            "pot": record["pot"],
            "en": record["en"],
            "audio_urls": record["audio_urls"],
            "word_lists": record["word_lists"],
            "timestamp": time.time(),
        }

        new_count += 1

        log.info(
            "[FOUND] %s | %s | audio=%d",
            record["pot"],
            record["en"],
            len(record["audio_urls"]),
        )

        # Write after every successful entry.
        write_tmx(tree)
        save_state(state)

        time.sleep(delay)

    return new_count, failed_count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Crawl Potawatomi dictionary entries from "
            "Wiwkwébthëgen into TMX."
        )
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=(
            f"Delay between requests in seconds "
            f"(default: {DEFAULT_DELAY})"
        ),
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help=(
            "Only scan this many dictionary pages. "
            "Useful for testing."
        ),
    )

    parser.add_argument(
        "--max-entries",
        type=int,
        default=None,
        help=(
            "Only process this many pending dictionary entries."
        ),
    )

    parser.add_argument(
        "--rediscover",
        action="store_true",
        help=(
            "Re-scan dictionary pagination even if pages "
            "already exist in the state file."
        ),
    )

    parser.add_argument(
        "--reset-state",
        action="store_true",
        help=(
            "Delete the crawler state and start discovery again. "
            "Does NOT delete the TMX."
        ),
    )

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # State
    # -----------------------------------------------------------------------

    if args.reset_state and os.path.exists(WORK_JSON):
        os.remove(WORK_JSON)

        log.info(
            "Removed state file: %s",
            WORK_JSON,
        )

    state = load_state()

    if args.rediscover:
        state["scanned_pages"] = {}

    # -----------------------------------------------------------------------
    # TMX
    # -----------------------------------------------------------------------

    tree = ensure_tmx(
        TMX_FILE
    )

    log.info(
        "TMX file: %s",
        TMX_FILE,
    )

    log.info(
        "State file: %s",
        WORK_JSON,
    )

    # -----------------------------------------------------------------------
    # Session
    # -----------------------------------------------------------------------

    session = create_session()

    try:

        # ---------------------------------------------------------------
        # Discover all dictionary pages / word URLs
        # ---------------------------------------------------------------

        discover_dictionary(
            session,
            state,
            delay=args.delay,
            max_pages=args.max_pages,
        )

        save_state(state)

        # ---------------------------------------------------------------
        # Limit entries if requested
        # ---------------------------------------------------------------

        if args.max_entries is not None:

            processed = state["processed_urls"]

            pending = [
                url
                for url in state["discovered_urls"]
                if url not in processed
            ]

            allowed = set(
                pending[:args.max_entries]
            )

            original_discovered = (
                state["discovered_urls"]
            )

            state["discovered_urls"] = {
                url: metadata
                for url, metadata
                in original_discovered.items()
                if (
                    url in processed
                    or url in allowed
                )
            }

        # ---------------------------------------------------------------
        # Crawl entries
        # ---------------------------------------------------------------

        new_count, failed_count = crawl_entries(
            session,
            state,
            tree,
            delay=args.delay,
        )

        state["last_run"] = {
            "timestamp": time.time(),
            "new_entries": new_count,
            "failed_entries": failed_count,
            "discovered_entries": len(
                state["discovered_urls"]
            ),
            "processed_entries": len(
                state["processed_urls"]
            ),
        }

        save_state(state)

        # Final TMX write.
        write_tmx(tree)

        log.info(
            "--------------------------------------------------"
        )

        log.info(
            "Crawl complete."
        )

        log.info(
            "Discovered: %d",
            len(state["discovered_urls"]),
        )

        log.info(
            "Processed: %d",
            len(state["processed_urls"]),
        )

        log.info(
            "New TMX entries this run: %d",
            new_count,
        )

        log.info(
            "Failed/unparsed: %d",
            failed_count,
        )

        log.info(
            "Output: %s",
            TMX_FILE,
        )

    except KeyboardInterrupt:

        log.warning(
            "Interrupted. State has been saved incrementally."
        )

        save_state(state)

        try:
            write_tmx(tree)
        except Exception:
            pass

        raise


if __name__ == "__main__":
    main()
