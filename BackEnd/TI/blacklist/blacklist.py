import requests

API_KEY = "HSl5cpao1as3snxfzRrWW7LQ7YPoeIki"
BASE_URL = "https://www.blacklistmaster.com/restapi/v1/blacklistcheck/ip"

def check_ip_blacklist(ip):
    url = f"{BASE_URL}/{ip}?apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "Blacklisted":
                print(f"IP {ip} is blacklisted.")
                print(f"Blacklists: {data.get('blacklist_cnt')} | Severity: {data.get('blacklist_severity')}")
                for bl in data.get("blacklists", []):
                    print(f"- {bl['blacklist_name']} ({bl['blacklist_url']})")
            else:
                print(f"IP {ip} is NOT blacklisted.")
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    ip_to_check = input("Enter IP address to check: ").strip()
    check_ip_blacklist(ip_to_check)
