import os
import json
from flask import Blueprint, request, jsonify

mitre_bp = Blueprint('mitre', __name__)

# Fayl yolu
json_path = os.path.join(os.path.dirname(__file__), 'data', 'enterprise-attack.json')
with open(json_path, 'r', encoding='utf-8') as f:
    attack_data = json.load(f)

# ===================== PARSING =====================
techniques = []
groups = []
software = []
mitigations = []
tactics = []
matrices = []
data_components = []
kc_phases = set()

for obj in attack_data['objects']:
    type_ = obj.get("type")
    ext_id = next((r.get("external_id") for r in obj.get("external_references", []) if r.get("source_name") == "mitre-attack"), "")

    if type_ == "attack-pattern":
        techniques.append({
            "type": "technique",
            "name": obj.get("name", ""),
            "id": ext_id,
            "description": obj.get("description", ""),
            "platforms": obj.get("x_mitre_platforms", []),
            "kill_chain_phases": obj.get("kill_chain_phases", []),
            "data_sources": obj.get("x_mitre_data_sources", [])
        })

        for phase in obj.get("kill_chain_phases", []):
            kc_phases.add(phase.get("phase_name", "").lower())

    elif type_ == "intrusion-set":
        groups.append({
            "type": "group",
            "name": obj.get("name", ""),
            "id": ext_id,
            "description": obj.get("description", "")
        })

    elif type_ in ["tool", "malware"]:
        software.append({
            "type": "software",
            "name": obj.get("name", ""),
            "id": ext_id,
            "description": obj.get("description", "")
        })

    elif type_ == "course-of-action":
        mitigations.append({
            "type": "mitigation",
            "name": obj.get("name", ""),
            "id": ext_id,
            "description": obj.get("description", "")
        })

    elif type_ == "x-mitre-tactic":
        tactics.append({
            "type": "tactic",
            "name": obj.get("name", ""),
            "id": ext_id,
            "description": obj.get("description", "")
        })

    elif type_ == "x-mitre-matrix":
        matrices.append({
            "type": "matrix",
            "name": obj.get("name", ""),
            "id": ext_id,
            "description": obj.get("description", "")
        })

    elif type_ == "x-mitre-data-component":
        data_components.append({
            "type": "data_component",
            "name": obj.get("name", ""),
            "id": ext_id,
            "description": obj.get("description", "")
        })

# ===================== ROUTES =====================

@mitre_bp.route('/api/techniques', methods=['GET'])
def get_techniques():
    return jsonify(techniques)


@mitre_bp.route('/api/mitre/search')
def search_mitre_data():
    query = request.args.get('query', '').lower()
    filter_type = request.args.get('type', '').lower()

    results = []
    seen_ids = set()

    databases = [
        ('technique', techniques),
        ('group', groups),
        ('software', software),
        ('mitigation', mitigations),
        ('tactic', tactics),
        ('matrix', matrices),
        ('data_component', data_components)
    ]

    for db_name, db in databases:
        if filter_type and filter_type != db_name:
            continue
        for obj in db:
            obj_id = obj.get("id", "").lower()
            name = obj.get("name", "").lower()
            ext_id = obj.get("id", "").lower()

            if obj_id in seen_ids:
                continue

            # === Əgər query boşdursa vəya uyğunluq varsa ===
            if not query or query in name or query in ext_id:
                obj['type'] = db_name
                results.append(obj)
                seen_ids.add(obj_id)

    # Kill chain axtarışı (yalnız uyğun tip seçilərsə vəya boşdursa)
    if not filter_type or filter_type == "killchain":
        for phase in kc_phases:
            if not query or query in phase:
                results.append({
                    "type": "killchain",
                    "name": phase,
                    "id": "",  # link olmadığı üçün boş verilir
                    "description": ""
                })

    return jsonify(results)