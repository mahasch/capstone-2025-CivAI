import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re
import time
import threading
from queue import Queue

COUNCILS = {
    "barking_and_dagenham": "https://www.lbbd.gov.uk",
    "barnet": "https://www.barnet.gov.uk",
    "bexley": "https://www.bexley.gov.uk",
    "brent": "https://www.brent.gov.uk",
    "bromley": "https://www.bromley.gov.uk",
    "ealing": "https://www.ealing.gov.uk",
    "enfield": "https://www.enfield.gov.uk",
    "greenwich": "https://www.royalgreenwich.gov.uk",
    "hackney": "https://www.hackney.gov.uk",
    "hammersmith_and_fulham": "https://www.lbhf.gov.uk",
    "haringey": "https://www.haringey.gov.uk",
    "harrow": "https://www.harrow.gov.uk",
    "havering": "https://www.havering.gov.uk",
    "hillingdon": "https://www.hillingdon.gov.uk",
    "hounslow": "https://www.hounslow.gov.uk",
    "islington": "https://www.islington.gov.uk",
    "kensington_and_chelsea": "https://www.rbkc.gov.uk",
    "kingston_upon_thames": "https://www.kingston.gov.uk",
    "lewisham": "https://www.lewisham.gov.uk",
    "merton": "https://www.merton.gov.uk",
    "newham": "https://www.newham.gov.uk",
    "redbridge": "https://www.redbridge.gov.uk",
    "richmond_upon_thames": "https://www.richmond.gov.uk",
    "sutton": "https://www.sutton.gov.uk",
    "tower_hamlets": "https://www.towerhamlets.gov.uk",
    "waltham_forest": "https://www.walthamforest.gov.uk",
    "wandsworth": "https://www.wandsworth.gov.uk",
    "westminster": "https://www.westminster.gov.uk",

}


KEYWORDS = [
    "services", "about", "accessibility", "adult", "benefits",
    "births", "deaths", "business", "licensing", "children",
    "community", "covid", "council tax", "emergencies",
    "environment", "housing", "libraries", "parking",
    "planning", "schools", "recycling", "transport",
    "tenants", "voting", "elections"
]

EXPAND_WORDS = ["see more", "see all", "show more", "view all"]

BLOCKED_PATTERNS = [
    "calendar", "?page=", "filter", "search", "/events",
    ".jpg", ".png", ".css", ".js"
]

MAX_PAGES = 300
DELAY = 0.2
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CouncilCrawler/1.0)"}

print_lock = threading.Lock()

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def same_domain(url, domain):
    parsed = urlparse(url)
    return domain in parsed.netloc or parsed.netloc == ""

def is_blocked(url):
    return any(p in url.lower() for p in BLOCKED_PATTERNS)

def log(msg):
    with print_lock:
        print(msg)

def crawl_site(name, start_url):
    log(f"\n=== {name.upper()} ===")
    domain = urlparse(start_url).netloc

    visited = set()
    to_visit = Queue()
    to_visit.put(start_url)

    pdf_links = set()
    pages_count = 0

    os.makedirs(f"downloads/{name}", exist_ok=True)

    while not to_visit.empty() and pages_count < MAX_PAGES:
        url = to_visit.get()

        if url in visited or is_blocked(url):
            continue

        visited.add(url)
        pages_count += 1

        log(f"[{name}] {pages_count}/{MAX_PAGES} -> {url}")

        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                continue
        except:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True).lower()
            full_url = urljoin(url, href)
            combined = (text + " " + href).lower()

            # Collect PDFs
            if full_url.lower().endswith(".pdf"):
                pdf_links.add(full_url)
                continue

            # Follow relevant links
            if any(k in combined for k in KEYWORDS) or any(w in combined for w in EXPAND_WORDS):
                if same_domain(full_url, domain) and not is_blocked(full_url):
                    if full_url not in visited:
                        to_visit.put(full_url)

        time.sleep(DELAY)

    log(f"✅ {name}: Found {len(pdf_links)} PDFs")

    # Download PDFs (also inside each thread)
    for pdf_url in pdf_links:
        try:
            filename = sanitize_filename(pdf_url.split("/")[-1])
            path = f"downloads/{name}/{filename}"

            if os.path.exists(path):
                continue

            r = requests.get(pdf_url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
        except:
            continue


if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)

    threads = []

    for name, url in COUNCILS.items():
        t = threading.Thread(target=crawl_site, args=(name, url))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print("\n✅ All councils finished.")
