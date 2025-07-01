from flask import Blueprint, jsonify
import requests
from bs4 import BeautifulSoup

mitre_bp = Blueprint('mitre', __name__)

@mitre_bp.route("/api/mitre-live")
def mitre_live():
    try:
        url = "https://attack.mitre.org/matrices/enterprise/"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        tactic_divs = soup.select("div.tactic-row")
        output = []

        for tactic_div in tactic_divs:
            tactic_title = tactic_div.select_one(".tactic-title")
            if not tactic_title:
                continue

            tactic = tactic_title.text.strip()
            techniques = [
                el.text.strip()
                for el in tactic_div.select("div.technique span.technique-name")
                if el.text.strip()
            ]
            output.append({"tactic": tactic, "techniques": techniques})

        if not output:
            return jsonify({"error": "❌ No techniques were found in MITRE matrix."})
        return jsonify(output)

    except Exception as e:
        return jsonify({"error": f"❌ Failed to load MITRE data: {str(e)}"})
