import requests
from bs4 import BeautifulSoup

def scrape_shodan_host(ip):
    url = f"https://www.shodan.io/host/{ip}"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch page: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- Hostname / IP ---
    ip_address = "N/A"
    host_label = soup.find("label", string="Hostnames")
    if host_label:
        hostname_div = host_label.find_next_sibling("div")
        if hostname_div:
            ip_address = hostname_div.text.strip()

    # --- Ports ---
    ports = []
    ports_div = soup.find("div", id="ports")
    if ports_div:
        ports = [a.text.strip() for a in ports_div.find_all("a") if a.text.strip().isdigit()]

    # --- Vulnerabilities ---
    vulnerabilities = []
    vulns_table = soup.find("div", id="vulns-table")
    if vulns_table:
        vuln_divs = vulns_table.select("div.vuln-row")
        vulnerabilities = [div.get('id') for div in vuln_divs if div.get('id', '').startswith('CVE-')]

    # --- Check if both ports and vulnerabilities are empty ---
    if not ports and not vulnerabilities:
        print("There is no information about this IP")
        return None

    # --- Result ---
    return {
        "ip": ip_address,
        "ports": ports,
        #"banners": banners,
        "vulnerabilities": vulnerabilities
    }

# --- Example usage ---
if __name__ == "__main__":
    ip = input("Enter IP address to search on Shodan: ").strip()
    result = scrape_shodan_host(ip)

    if result:
        print("\n📊 Parsed Shodan Result:")
        for key, value in result.items():
            print(f"{key.capitalize()}: {value if value else 'None'}")
