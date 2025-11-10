import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = f"{BASE_URL}/products/product-catalog/"

def scrape_page(offset=0):
    """
    Scrapes one catalog page of 'Individual Test Solutions'.
    """
    params = {"start": offset, "type": 1, "type": 1}
    res = requests.get(CATALOG_URL, params=params, timeout=15)
    if res.status_code != 200:
        print(f"Failed to load page at offset {offset}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("div.custom__table-responsive table tr[data-entity-id]")
    if not rows:
        return []

    data = []
    for row in rows:
        name_tag = row.select_one("td.custom__table-heading__title a")
        if not name_tag:
            continue

        name = name_tag.get_text(strip=True)
        relative_url = name_tag.get("href", "")
        full_url = f"{BASE_URL}{relative_url}" if relative_url.startswith("/") else relative_url

        # Extract test type keys like A, E, B, etc.
        type_keys = [span.get_text(strip=True) for span in row.select("td.product-catalogue__keys span.product-catalogue__key")]
        type_str = ", ".join(type_keys)

        # Remote testing flag (green circle)
        remote_test = bool(row.select_one("td:nth-of-type(2) .catalogue__circle.-yes"))

        # Adaptive/IRT flag
        adaptive = bool(row.select_one("td:nth-of-type(3) .catalogue__circle.-yes"))

        data.append({
            "assessment_name": name,
            "url": full_url,
            "remote_testing": remote_test,
            "adaptive": adaptive,
            "test_type": type_str
        })

    return data


def scrape_all_assessments(step=12, max_pages=100):
    """
    Automatically paginates through catalog using ?start=<offset>.
    Stops when a page has no results.
    """
    all_results = []
    for page_num in tqdm(range(max_pages), desc="Scraping SHL pages"):
        offset = page_num * step
        items = scrape_page(offset)
        if not items:
            print(f"No results found at offset {offset}. Stopping.")
            break
        all_results.extend(items)
        time.sleep(1)

    df = pd.DataFrame(all_results).drop_duplicates(subset=["assessment_name"])
    df.to_csv("./data/shl_individual_test_solutions.csv", index=False)
    print(f"Scraped {len(df)} unique assessments total.")
    return df


if __name__ == "__main__":
    df = scrape_all_assessments()
    print(df.head())
