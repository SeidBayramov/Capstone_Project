import requests

def generate_usernames(name):
    # Basic username patterns from full name
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
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        # Instagram may block or throttle requests — handle carefully
        print(f"Got status {response.status_code} for {url}")
        return False

if __name__ == "__main__":
    name = "Omar Verdizada"
    print(f"Generating possible Instagram usernames for '{name}':")
    usernames = generate_usernames(name)

    print("Checking which usernames exist on Instagram...\n")
    found = []

    for username in usernames:
        if check_instagram_user(username):
            print(f"Found: https://www.instagram.com/{username}/")
            found.append(username)

    if not found:
        print("No Instagram profiles found for the generated usernames.")
