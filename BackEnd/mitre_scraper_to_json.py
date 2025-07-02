# mitre_scraper_to_json.py
import requests
from bs4 import BeautifulSoup
import json

def scrape_and_save_mitre_data(output_path="mitre_data.json"):
    url = "https://attack.mitre.org/matrices/enterprise/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    tactic_divs = soup.select("div.tactic-row")
    all_data = []

    for tactic_div in tactic_divs:
        tactic_name = tactic_div.select_one(".tactic-title")
        if tactic_name:
            tactic = tactic_name.text.strip()
            technique_items = tactic_div.select("div.technique span.technique-name")
            techniques = [item.text.strip() for item in technique_items if item.text.strip()]
            all_data.append({"tactic": tactic, "techniques": techniques})

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"[✔] MITRE data saved to {output_path}")

if __name__ == "__main__":
    scrape_and_save_mitre_data()
