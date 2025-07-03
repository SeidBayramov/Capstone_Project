import os, sys
from flask import Blueprint, request, jsonify

# TI qovluğunu path-ə əlavə et
ti_path = os.path.join(os.path.dirname(__file__), 'TI')
sys.path.append(ti_path)

# run_all funksiyasını əlavə edirik
from TI.ip_threat_logic import run_all


# Flask Blueprint
ip_threat_bp = Blueprint("ip_threat", __name__)

@ip_threat_bp.route("/api/ip_threat")
def ip_threat():
    ip = request.args.get("ip")
    if not ip:
        return jsonify({"error": "IP address required"}), 400

    try:
        results = run_all(ip)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
