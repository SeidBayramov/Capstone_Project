import requests

def vt_ip_info(ip, api_key):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {
        "x-apikey": api_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ VirusTotal API error: {response.status_code} - {response.text}")
        return None
    
    return response.json()

if __name__ == "__main__":
    api_key = "ae3702f43b8959e352aa028231c3f6b3335bb66d99c52e957ec8c7defbc06fa8"
    ip = input("Enter IP address to query: ").strip()

    data = vt_ip_info(ip, api_key)
    if data:
        print(f"VirusTotal info for IP {ip}:")
        # For demo, just print raw JSON keys and basic info:
        attributes = data.get("data", {}).get("attributes", {})
        reputation = attributes.get("reputation")
        as_owner = attributes.get("as_owner")
        last_analysis_stats = attributes.get("last_analysis_stats", {})
        country = attributes.get("country")

        print(f"Reputation: {reputation}")
        print(f"AS Owner: {as_owner}")
        print(f"Country: {country}")
        print("Last Analysis Stats:")
        for k,v in last_analysis_stats.items():
            print(f"  {k}: {v}")
    else:
        print("No data received.")
