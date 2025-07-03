import requests
import concurrent.futures
from bs4 import BeautifulSoup

# === API KEYS ===
ABUSEIPDB_API_KEY = "52058768e30892fa3524c4b610ca1f7beecadbd0888c69140a5180c409ce8469ace46fafd61c1582"
BLACKLISTMASTER_API_KEY = "HSl5cpao1as3snxfzRrWW7LQ7YPoeIki"
VT_API_KEY = "ae3702f43b8959e352aa028231c3f6b3335bb66d99c52e957ec8c7defbc06fa8"

# === 1. AbuseIPDB ===
def check_abuseipdb(ip):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        'Accept': 'application/json',
        'Key': ABUSEIPDB_API_KEY
    }
    params = {
        'ipAddress': ip,
        'maxAgeInDays': 90
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json().get('data', {})
            return {
                "status": "ok",
                "ip": data.get('ipAddress'),
                "abuse_score": data.get('abuseConfidenceScore'),
                "total_reports": data.get('totalReports'),
                "last_report": data.get('lastReportedAt')
            }
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === 2. BlacklistMaster ===
def check_blacklistmaster(ip):
    url = f"https://www.blacklistmaster.com/restapi/v1/blacklistcheck/ip/{ip}?apikey={BLACKLISTMASTER_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "ok",
                "blacklisted": data.get("status") == "Blacklisted",
                "count": data.get("blacklist_cnt"),
                "severity": data.get("blacklist_severity"),
                "blacklists": data.get("blacklists", [])
            }
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === 3. VirusTotal ===
def check_virustotal(ip):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {
        "x-apikey": VT_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            attributes = response.json().get("data", {}).get("attributes", {})
            return {
                "status": "ok",
                "reputation": attributes.get("reputation"),
                "country": attributes.get("country"),
                "as_owner": attributes.get("as_owner"),
                "last_analysis": attributes.get("last_analysis_stats", {})
            }
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === 4. Shodan (no key, HTML parse) ===
def check_shodan(ip):
    url = f"https://www.shodan.io/host/{ip}"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"status": "error", "message": f"HTTP {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')
        ports = []
        ports_div = soup.find("div", id="ports")
        if ports_div:
            ports = [a.text.strip() for a in ports_div.find_all("a") if a.text.strip().isdigit()]

        vulnerabilities = []
        vulns_table = soup.find("div", id="vulns-table")
        if vulns_table:
            vuln_divs = vulns_table.select("div.vuln-row")
            vulnerabilities = [div.get('id') for div in vuln_divs if div.get('id', '').startswith('CVE-')]

        return {
            "status": "ok",
            "ip": ip,
            "ports": ports,
            "vulnerabilities": vulnerabilities
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === Run All in Parallel ===
def run_all(ip):
    results = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_tool = {
            executor.submit(check_abuseipdb, ip): "abuseipdb",
            executor.submit(check_blacklistmaster, ip): "blacklistmaster",
            executor.submit(check_virustotal, ip): "virustotal",
            executor.submit(check_shodan, ip): "shodan"
        }

        for future in concurrent.futures.as_completed(future_to_tool):
            tool = future_to_tool[future]
            try:
                results[tool] = future.result()
            except Exception as exc:
                results[tool] = {"status": "error", "message": str(exc)}

    return results

def get_ip_threat_report(ip):
    return run_all(ip)

# === Entry Point ===
if __name__ == "__main__":
    ip = input("Enter IP address to check: ").strip()
    results = run_all(ip)

    print("\n📊 Combined IP Threat Report:\n")
    for source, data in results.items():
        print(f"🔹 {source.upper()}")
        if data["status"] == "ok":
            for k, v in data.items():
                if k != "status":
                    print(f"  {k}: {v}")
        else:
            print(f"  ❌ Error: {data['message']}")
        print()
