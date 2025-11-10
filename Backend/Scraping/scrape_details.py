import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import io
import pandas as pd
from tqdm import tqdm
import time


def extract_pdf_text_from_url(pdf_url):
    """
    Fetch PDF directly from the URL and extract text (in-memory).
    """
    try:
        response = requests.get(pdf_url, timeout=25)
        response.raise_for_status()

        pdf_data = io.BytesIO(response.content)
        reader = PdfReader(pdf_data)

        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text.strip()

    except Exception as e:
        print(f"PDF extraction failed for {pdf_url}: {e}")
        return ""


def get_fact_sheet_url(page_url):
    """
    Find 'Fact Sheet' PDF link from a given SHL product page.
    """
    base_url = "https://www.shl.com"
    if page_url.startswith("/"):
        page_url = base_url + page_url

    try:
        res = requests.get(page_url, timeout=25)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select(".product-catalogue__downloads a")
        for a in links:
            text = a.get_text(strip=True).lower()
            href = a.get("href", "")
            if "fact sheet" in text and href.endswith(".pdf"):
                if href.startswith("http"):
                    return href
                else:
                    return "https://www.shl.com" + href
    except Exception as e:
        print(f"Error scraping {page_url}: {e}")
        return None

    return None


def scrape_shl_fact_sheets(input_csv="shl_individual_test_solutions.csv", output_csv="shl_fact_sheets_text.csv"):
    """
    Main function:
    - Reads URLs from input CSV (should have a column 'url')
    - Scrapes each page for a Fact Sheet PDF link
    - Extracts PDF text (in-memory)
    - Saves to output CSV
    """
    df = pd.read_csv(input_csv)

    df["fact_sheet_url"] = ""
    df["fact_sheet_text"] = ""

    for i, row in tqdm(df.iterrows(), total=len(df), desc="Scraping SHL PDFs"):
        url = str(row["url"]).strip()
        if not url:
            continue

        fact_sheet_url = get_fact_sheet_url(url)
        df.loc[i, "fact_sheet_url"] = fact_sheet_url or ""

        if fact_sheet_url:
            text = extract_pdf_text_from_url(fact_sheet_url)
            df.loc[i, "fact_sheet_text"] = text
        else:
            df.loc[i, "fact_sheet_text"] = ""

        time.sleep(1.5)

    df.to_csv(output_csv, index=False)
    print(f"Done! Extracted data saved to: {output_csv}")


if __name__ == "__main__":
    scrape_shl_fact_sheets()
