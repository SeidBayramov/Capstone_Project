import requests
import re
from bs4 import BeautifulSoup
from googlesearch import search
import time

# ========== GOOGLE DORK ==========
def google_dork_search(query):
    try:
        return list(search(query, lang="en"))  # removed num_results
    except Exception as e:
        print(f"Google search error: {e}")
        return []

# ========== GITHUB SEARCH ==========
def github_search(name):
    parts = name.split()
    queries = [name] + parts
    found_users = {}

    for q in queries:
        url = f"https://api.github.com/search/users?q={q}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            users = data.get("items", [])
            for u in users[:5]:
                found_users[u["login"]] = u["html_url"]
        else:
            print(f"[!] GitHub API error for '{q}': {response.status_code}")

    return [{"login": login, "url": url} for login, url in found_users.items()]

# ========== INSTAGRAM USERNAME CHECK ==========
def generate_usernames(name):
    parts = name.lower().split()
    usernames = set()
    if len(parts) == 1:
        usernames.add(parts[0])
    elif len(parts) >= 2:
        first, last = parts[0], parts[-1]
        usernames.update([
            first + last,
            first + '.' + last,
            first + '_' + last,
            first[0] + last,
            first + last[0],
            last + first,
            last + '.' + first,
            last + '_' + first,
            first,
            last,
        ])
    return usernames

def check_instagram_user(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/113.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200

# ========== DUCKDUCKGO SCRAPER (emails, phones) ==========
def extract_visible_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'svg', 'meta', 'link']):
        tag.decompose()
    return soup.get_text(separator=' ', strip=True)

def extract_emails(text):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    return list(set(re.findall(email_regex, text)))

def extract_phones(text):
    phone_regex = r'\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b'
    phones = re.findall(phone_regex, text)
    return [p for p in phones if re.search(r'^\d{7,}$', p) is None]

def search_duckduckgo(query):
    url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return extract_visible_text(response.text)

# ========== LINKEDIN SEARCH ==========
def search_linkedin_profiles(name):
    queries = [
        f'site:linkedin.com/in "{name}"',
        f'site:linkedin.com/pub "{name}"',
    ]
    found_profiles = set()

    print(f"\n--- Searching Google for LinkedIn profiles of '{name}' ---")
    for query in queries:
        print(f"\nSearching Google for query: {query}")
        try:
            for url in search(query, lang="en"):  # removed num_results
                if "linkedin.com/in/" in url or "linkedin.com/pub/" in url:
                    found_profiles.add(url)
            time.sleep(10)
        except Exception as e:
            print(f"Search failed: {e}")

    if found_profiles:
        print("\nLinkedIn profiles found:")
        for profile in found_profiles:
            print(f"- {profile}")
    else:
        print("No LinkedIn profiles found.")

    return list(found_profiles)

# ========== MAIN ==========
if __name__ == "__main__":
    name = input("Enter the name of the person (e.g., Nurlan Isazade): ").strip()

    print("\n--- GitHub Results ---")
    github_users = github_search(name)
    for user in github_users:
        print(f"- {user['login']}: {user['url']}")
    if not github_users:
        print("No GitHub profiles found.")

    print("\n--- Instagram Results ---")
    usernames = generate_usernames(name)
    found_insta = []
    for username in usernames:
        if check_instagram_user(username):
            print(f"- https://www.instagram.com/{username}/")
            found_insta.append(username)
    if not found_insta:
        print("No Instagram profiles found.")

    print("\n--- Searching DuckDuckGo for emails and phone numbers ---")
    ddg_text = search_duckduckgo(f'"{name}" email OR contact')
    emails = extract_emails(ddg_text)
    phones = extract_phones(ddg_text)

    print("\nEmails found:")
    if emails:
        for e in emails:
            print(f"- {e}")
    else:
        print("No emails found.")

    print("\nPhone numbers found:")
    if phones:
        for p in phones:
            print(f"- {p}")
    else:
        print("No phone numbers found.")

    print("\n--- Linkedin ---")
    search_linkedin_profiles(name)
