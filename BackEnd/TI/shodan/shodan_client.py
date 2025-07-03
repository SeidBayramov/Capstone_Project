import shodan

# Replace this with your actual Shodan API key
SHODAN_API_KEY = "XejKc4iCssjq1BoXAOsWRSpA2VwG6BMC"

# Create API instance
api = shodan.Shodan(SHODAN_API_KEY)

def search_ip_shodan(ip_address):
    try:
        result = api.host(ip_address)

        # Extract useful info
        parsed_result = {
            "IP": result.get("ip_str", ""),
            "Organization": result.get("org", "N/A"),
            "ISP": result.get("isp", "N/A"),
            "Operating System": result.get("os", "N/A"),
            "Hostnames": result.get("hostnames", []),
            "City": result.get("city", ""),
            "Country": result.get("country_name", ""),
            "Tags": result.get("tags", []),
            "Last Update": result.get("last_update", ""),
            "Open Ports": result.get("ports", []),
            "Vulnerabilities": [],
            "Services": []
        }

        # Collect services and banners
        for service in result.get("data", []):
            parsed_service = {
                "Port": service.get("port"),
                "Transport": service.get("_shodan", {}).get("transport", ""),
                "Banner": service.get("data", "")[:200],  # Limit to 200 chars
                "Product": service.get("product", ""),
                "Version": service.get("version", "")
            }
            parsed_result["Services"].append(parsed_service)

            # Collect vulnerabilities if any
            vulns = service.get("vulns", [])
            if isinstance(vulns, dict):
                parsed_result["Vulnerabilities"].extend(list(vulns.keys()))
            elif isinstance(vulns, list):
                parsed_result["Vulnerabilities"].extend(vulns)

        return parsed_result

    except shodan.APIError as e:
        return {"error": str(e)}

# === Example usage ===
if __name__ == "__main__":
    ip = input("Enter IP address to search on Shodan: ")
    result = search_ip_shodan(ip)

    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("\n🛰️  Shodan Search Results")
        print("-" * 40)
        for key, value in result.items():
            if isinstance(value, list):
                print(f"{key}:")
                for item in value:
                    print(f"  - {item}")
            else:
                print(f"{key}: {value}")
