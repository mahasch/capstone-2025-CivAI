import os
import time
import requests
from urllib.parse import urljoin, urlparse
from threading import Thread, Lock
from xml.etree import ElementTree
from bs4 import BeautifulSoup, Comment, NavigableString
from fpdf import FPDF

# ======================== CONFIG ========================
COUNCILS = {
  "barking-and-dagenham":    "https://www.lbbd.gov.uk",
  "barnet":                  "https://www.barnet.gov.uk",
  "bexley":                  "https://www.bexley.gov.uk",
  "brent":                   "https://www.brent.gov.uk",
  "bromley":                 "https://www.bromley.gov.uk",
  "camden":                  "https://www.camden.gov.uk",
  "croydon":                 "https://www.croydon.gov.uk",
  "ealing":                  "https://www.ealing.gov.uk",
  "greenwich":               "https://www.royalgreenwich.gov.uk",
  "hammersmith-and-fulham":  "https://www.lbhf.gov.uk",
  "haringey":                "https://www.haringey.gov.uk",
  "harrow":                  "https://www.harrow.gov.uk",
  "havering":                "https://www.havering.gov.uk",
  "hillingdon":              "https://www.hillingdon.gov.uk",
  "hounslow":                "https://www.hounslow.gov.uk",
  "islington":               "https://www.islington.gov.uk",
  "kensington-and-chelsea":  "https://www.rbkc.gov.uk",
  "kingston-upon-thames":    "https://www.kingston.gov.uk",
  "lambeth":                 "https://www.lambeth.gov.uk",
  "lewisham":                "https://www.lewisham.gov.uk",
  "merton":                  "https://www.merton.gov.uk",
  "newham":                  "https://www.newham.gov.uk",
  "redbridge":               "https://www.redbridge.gov.uk",
  "richmond-upon-thames":    "https://www.richmond.gov.uk",
  "southwark":               "https://www.southwark.gov.uk",
  "sutton":                  "https://www.sutton.gov.uk",
  "tower-hamlets":           "https://www.towerhamlets.gov.uk",
  "waltham-forest":          "https://www.walthamforest.gov.uk",
  "wandsworth":              "https://www.wandsworth.gov.uk",
  "westminster":             "https://www.westminster.gov.uk"
}


MAX_PAGES = 100

BLOCKED_PATTERNS = [
    "/news", "/events", "/blog", "/press", "/media",
    "/jobs", "/careers", "/leisure", "/whatson",
    "/library", "/libraries", "/sports",
    "/covid", "/coronavirus", "/newsletter",
    "/subscribe", "/whats-on"
]

ALLOWED_KEYWORDS = [
    "/services", "/service", "/council", "/your-council", "/democracy",
    "/voting", "/vote", "/election", "/elections", "/register-to-vote",
    "/council-tax", "/tax", "/benefit", "/benefits",
    "/housing", "/homeless", "/planning", "/building",
    "/waste", "/rubbish", "/recycling", "/bins",
    "/parking", "/permit", "/licens",
    "/children", "/family", "/adult", "/social-care",
    "/business", "/licensing",
    "/complaint", "/complaints", "/feedback",
    "/contact", "/contact-us", "/about",
    "/apply", "/report", "/request", "/form"
]

BOILERPLATE_WORDS = [
    "cookie", "privacy", "terms", "subscribe", "feedback",
    "translation", "accessibility", "search",
    "newsletter", "home -", "skip to content",
    "accept analytics cookies", "reject analytics cookies"
]

print_lock = Lock()

# ======================== HELPERS ========================
def log(msg):
    with print_lock:
        print(msg)

def safe(text):
    return text.encode("latin-1", "ignore").decode("latin-1")

def is_blocked(url):
    return any(p in url.lower() for p in BLOCKED_PATTERNS)

def is_allowed_url(url):
    path = urlparse(url).path.lower()
    if any(b in path for b in BLOCKED_PATTERNS):
        return False
    if any(k in path for k in ALLOWED_KEYWORDS):
        return True
    return False

def extract_content(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["header", "footer", "nav", "aside"]):
        tag.decompose()

    for text in soup.find_all(string=True):
        if isinstance(text, Comment):
            continue
        if isinstance(text, NavigableString) and getattr(text, "parent", None):
            if any(bp in text.lower() for bp in BOILERPLATE_WORDS):
                text.parent.decompose()

    headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"]) if h.get_text(strip=True)]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 30]
    for li in soup.find_all("li"):
        t = li.get_text(strip=True)
        if t and len(t) > 30:
            paragraphs.append(t)

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
    pdf.cell(0, 10, safe(name.upper() + " – COUNCIL SERVICES"), ln=True, align="C")

    for page in data:
        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 6, safe(page["url"]))

        for h in page["headings"]:
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 5, safe(h))

        for p in page["paragraphs"]:
            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(0, 5, safe(p))

        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    path = f"pdf_output/{name}.pdf"
    pdf.output(path)
    log(f"✅ Saved: {path}")

# ======================== CRAWLER ========================
def crawl(name, base_url):
    log(f"🚀 Starting {name}")
    visited = set()
    results = []

    # Try to find sitemap
    sitemap_url = urljoin(base_url, "/sitemap.xml")
    try:
        r = requests.get(sitemap_url, timeout=10)
        r.raise_for_status()
        root = ElementTree.fromstring(r.content)
        urls = [elem.text for elem in root.iter() if elem.tag.endswith("loc")]
    except:
        log(f"[{name}] Sitemap not found. Falling back to homepage only.")
        urls = [base_url]

    for url in urls:
        if url in visited or is_blocked(url) or not is_allowed_url(url):
            continue
        if len(visited) >= MAX_PAGES:
            break
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            visited.add(url)

            headings, paragraphs = extract_content(r.text)
            if meaningful(headings, paragraphs):
                results.append({
                    "url": url,
                    "headings": headings,
                    "paragraphs": paragraphs
                })
                log(f"[{name}] {len(visited)}/{MAX_PAGES} -> {url}")

        except Exception as e:
            log(f"[{name}] ERROR: {url} -> {e}")
            continue

    save_pdf(name, results)
    log(f"✅ Finished {name}")

# ======================== MAIN ========================
if __name__ == "__main__":
    threads = []
    for name, url in COUNCILS.items():
        t = Thread(target=crawl, args=(name, url))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    log("🎉 Done.")
