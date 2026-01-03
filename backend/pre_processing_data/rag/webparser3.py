import threading
import os
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

# ---------------------
# Configuration
# ---------------------
OUTPUT_DIR = "pdf_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Example council URLs
councils = [
    "https://www.lewisham.gov.uk",
    "https://www.southwark.gov.uk",
    "https://www.greenwich.gov.uk",
    "https://www.lambeth.gov.uk",
    "https://www.islington.gov.uk",
    "https://www.towerhamlets.gov.uk",
    "https://www.wandsworth.gov.uk",
    "https://www.haringey.gov.uk"
]

# ---------------------
# PDF saving function
# ---------------------
def clean_text(text):
    """Replace characters that Latin-1 can't encode."""
    replacements = {
        "–": "-",  # en dash
        "—": "-",  # em dash
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "…": "...",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text

def save_pdf(name, results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)  # Default font

    for section, paragraphs in results.items():
        # Heading
        pdf.set_font("Arial", "B", 14)
        pdf.multi_cell(0, 8, clean_text(section))
        pdf.ln(4)

        # Paragraphs
        pdf.set_font("Arial", "", 12)
        for para in paragraphs:
            pdf.multi_cell(0, 6, clean_text(para))
            pdf.ln(2)

    pdf_file = os.path.join(OUTPUT_DIR, f"{name}.pdf")
    pdf.output(pdf_file)
    print(f"[{name}] PDF saved to {pdf_file}")

# ---------------------
# Web scraping function
# ---------------------
def crawl(url):
    name = url.split("//")[1].split(".")[0]  # simple name from URL
    print(f"🚀 Crawling {name}")

    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        results = {}

        # Collect headings (h2) and their paragraphs
        for h2 in soup.find_all("h2"):
            section = h2.get_text(strip=True)

            temp = []
            for sibling in h2.find_next_siblings():
                if sibling.name == "h2":
                    break
                if sibling.name == "p":
                    temp.append(sibling.get_text(strip=True))

            if temp:
                results[section] = temp

        save_pdf(name, results)

    except Exception as e:
        print(f"[{name}] Error: {e}")

# ---------------------
# Main threaded crawler
# ---------------------
threads = []

for url in councils:
    t = threading.Thread(target=crawl, args=(url,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("✅ Crawling complete")
