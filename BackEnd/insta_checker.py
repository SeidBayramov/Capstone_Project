# BackEnd/insta_checker.py
import requests

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
