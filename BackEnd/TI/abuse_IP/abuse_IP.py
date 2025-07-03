import requests

def check_ip_abuse(ip, api_key):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        'Accept': 'application/json',
        'Key': "52058768e30892fa3524c4b610ca1f7beecadbd0888c69140a5180c409ce8469ace46fafd61c1582"
    }
    params = {
        'ipAddress': ip,
        'maxAgeInDays': 90
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"❌ API request failed with status code {response.status_code}")
        return None

    data = response.json()
    return data.get('data', {})

if __name__ == "__main__":
    api_key = "52058768e30892fa3524c4b610ca1f7beecadbd0888c69140a5180c409ce8469ace46fafd61c1582"  # Replace with your AbuseIPDB API key
    ip = input("Enter IP address to check AbuseIPDB: ").strip()

    result = check_ip_abuse(ip, api_key)

    if not result or result.get('totalReports', 0) == 0:
        print("There is no information about this IP")
    else:
        print(f"IP Address: {result.get('ipAddress')}")
        print(f"Abuse Confidence Score: {result.get('abuseConfidenceScore')}")
        print(f"Total Reports: {result.get('totalReports')}")
        print(f"Last Reported: {result.get('lastReportedAt')}")
