import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from fpdf import FPDF
from threading import Thread
from queue import Queue
import time

# ======================== CONFIG ========================
COUNCILS = {
    "barking_and_dagenham":      "https://www.lbbd.gov.uk",
    "barnet":                    "https://www.barnet.gov.uk",
    "bexley":                    "https://www.bexley.gov.uk",
    "brent":                     "https://www.brent.gov.uk",
    "bromley":                   "https://www.bromley.gov.uk",
    "camden":                    "https://www.camden.gov.uk",
    "city_of_london":            "https://www.cityoflondon.gov.uk",
    "croydon":                   "https://www.croydon.gov.uk",
    "ealing":                    "https://www.ealing.gov.uk",
    "enfield":                   "https://www.enfield.gov.uk",
    "greenwich":                 "https://www.royalgreenwich.gov.uk",
    "hackney":                   "https://www.hackney.gov.uk",
    "hammersmith_and_fulham":    "https://www.lbhf.gov.uk",
    "haringey":                  "https://www.haringey.gov.uk",
    "harrow":                    "https://www.harrow.gov.uk",
    "havering":                  "https://www.havering.gov.uk",
    "hillingdon":                "https://www.hillingdon.gov.uk",
    "hounslow":                  "https://www.hounslow.gov.uk",
    "islington":                 "https://www.islington.gov.uk",
    "kensington_and_chelsea":    "https://www.rbkc.gov.uk",
    "kingston_upon_thames":      "https://www.kingston.gov.uk",
    # "lambeth":                   "https://www.lambeth.gov.uk",
    "lewisham":                  "https://www.lewisham.gov.uk",
    "merton":                    "https://www.merton.gov.uk",
    "newham":                    "https://www.newham.gov.uk",
    "redbridge":                 "https://www.redbridge.gov.uk",
    "richmond_upon_thames":      "https://www.richmond.gov.uk",
    "southwark":                 "https://www.southwark.gov.uk",
    "sutton":                    "https://www.sutton.gov.uk",
    "tower_hamlets":             "https://www.towerhamlets.gov.uk",
    "waltham_forest":            "https://www.walthamforest.gov.uk",
    "wandsworth":                "https://www.wandsworth.gov.uk",
    "westminster":               "https://www.westminster.gov.uk"
}


MAX_PAGES = 1000
DELAY = 0.05
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CouncilCrawler/1.0)"}

BLOCKED_PATTERNS = [
    ".jpg", ".png", ".css", ".js", "calendar", "filter",
    "/news", "/jobs", "/subscribe"
]

BOILERPLATE_WORDS = [
    "cookie", "privacy", "terms", "subscribe", "feedback",
    "translation", "accessibility", "search"
]

# ======================== HELPERS ========================
def is_blocked(url):
    return any(p in url.lower() for p in BLOCKED_PATTERNS)

def same_domain(url, domain):
    return urlparse(url).netloc.endswith(domain)

def safe(text):
    return text.encode("latin-1", "ignore").decode("latin-1")

def extract_content(soup):
    headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 30]
    return headings, paragraphs

def meaningful(headings, paragraphs):
    return len(headings) > 0 or len(paragraphs) >= 2

# ======================== PDF ========================
def save_pdf(name, data):
    os.makedirs("pdf_output", exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, safe(name.upper() + " COUNCIL CONTENT"), ln=True, align="C")

    for page in data:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 6, safe(page["url"]))

        for h in page["headings"]:
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 6, safe(h))

        for p in page["paragraphs"]:
            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(0, 5, safe(p))

        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    path = f"pdf_output/{name}_deepcrawl.pdf"
    pdf.output(path)
    print(f"✅ Saved: {path}")

# ======================== CRAWLER ========================
def crawl(name, start_url):
    domain = urlparse(start_url).netloc
    visited = set()
    q = Queue()
    q.put(start_url)
    results = []

    while not q.empty() and len(visited) < MAX_PAGES:
        url = q.get()
        if url in visited:
            continue
        visited.add(url)

        if is_blocked(url):
            continue

        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                continue
        except:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        # ====== SAVE CONTENT IF MEANINGFUL ======
        headings, paragraphs = extract_content(soup)
        if meaningful(headings, paragraphs):
            results.append({
                "url": url,
                "headings": headings,
                "paragraphs": paragraphs
            })
            print(f"[{name}] {len(visited)} -> {url}")

        # ====== TRUE DEEP TRAVERSAL ======
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            text = a.get_text(strip=True).lower()

            if link in visited:
                continue
            if link.endswith(".pdf"):
                continue
            if is_blocked(link):
                continue
            if not same_domain(link, domain):
                continue
            if any(b in text for b in BOILERPLATE_WORDS):
                continue

            q.put(link)

        time.sleep(DELAY)

    save_pdf(name, results)

# ======================== MAIN ========================
if __name__ == "__main__":
    threads = []
    for name, url in COUNCILS.items():
        t = Thread(target=crawl, args=(name, url))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("✅ Done.")
