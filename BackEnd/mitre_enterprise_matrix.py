"""
MITRE ATT&CK Command-Line Explorer (Full Version)
Supports: technique, group, software, mitigation, tactic, matrix, killchain, search
Author: FedMind
"""

import json
import sys

with open("enterprise-attack.json", "r", encoding="utf-8") as f:
    attack_data = json.load(f)

techniques_by_id = {}
groups_by_id = {}
software_by_id = {}
mitigations_by_id = {}
tactics_by_id = {}
matrices_by_id = {}
data_components_by_id = {}
relationships_by_source = {}
kc_phases = set()

# Pre-process all objects
for obj in attack_data["objects"]:
    ext_refs = obj.get("external_references", [])
    obj_id = next((r["external_id"] for r in ext_refs if r.get("source_name") == "mitre-attack"), None)
    name = obj.get("name", "")

    if obj.get("type") == "attack-pattern" and obj_id:
        techniques_by_id[obj_id.lower()] = obj
        techniques_by_id[name.lower()] = obj
    elif obj.get("type") == "intrusion-set" and obj_id:
        groups_by_id[obj_id.lower()] = obj
        groups_by_id[name.lower()] = obj
    elif obj.get("type") in ["tool", "malware"] and obj_id:
        software_by_id[obj_id.lower()] = obj
        software_by_id[name.lower().replace(" ", "")] = obj
    elif obj.get("type") == "course-of-action" and obj_id:
        mitigations_by_id[obj_id.lower()] = obj
        mitigations_by_id[name.lower()] = obj
    elif obj.get("type") == "x-mitre-tactic":
        ext_refs = obj.get("external_references", [])
        ext_id = next((r.get("external_id") for r in ext_refs if r.get("source_name") == "mitre-attack"), None)
        if ext_id:
            tactics_by_id[ext_id.lower()] = obj
        tactics_by_id[obj["name"].lower()] = obj
    elif obj.get("type") == "x-mitre-matrix":
        matrices_by_id[obj["name"].lower()] = obj
        for domain in obj.get("x_mitre_domains", []):
            matrices_by_id[domain.lower()] = obj
    elif obj.get("type") == "x-mitre-data-component" and name:
        data_components_by_id[name.lower()] = obj
    elif obj.get("type") == "relationship":
        src = obj.get("source_ref")
        if src not in relationships_by_source:
            relationships_by_source[src] = []
        relationships_by_source[src].append(obj)
    if obj.get("kill_chain_phases"):
        for kcp in obj["kill_chain_phases"]:
            kc_phases.add(kcp["phase_name"].lower())

def get_ext_id(obj):
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("external_id", "")
    return ""

def get_name_and_id(obj):
    return f"{obj.get('name')} ({get_ext_id(obj)})"

def display_technique(tech_id):
    obj = techniques_by_id.get(tech_id.lower())
    if not obj:
        print(f"[!] Technique not found: {tech_id}")
        return
    print(f"\n=== TECHNIQUE: {get_name_and_id(obj)} ===")
    print(f"Description:\n  {obj.get('description', '').strip()}")
    print(f"\nTactics:")
    for p in obj.get("kill_chain_phases", []):
        print(f"  - {p['phase_name']} ({p['kill_chain_name']})")
    print(f"\nPlatforms: {', '.join(obj.get('x_mitre_platforms', []))}")
    print(f"\nData Sources:")
    for ds in obj.get("x_mitre_data_sources", []):
        print(f"  - {ds}")

def display_group(identifier):
    obj = groups_by_id.get(identifier.lower())
    if not obj:
        print(f"[!] Group not found: {identifier}")
        return
    print(f"\n=== GROUP: {get_name_and_id(obj)} ===")
    print(f"Description:\n  {obj.get('description', '').strip()}")
    print(f"\nAssociated Techniques:")
    for rel in relationships_by_source.get(obj["id"], []):
        if rel["target_ref"].startswith("attack-pattern"):
            t = next((t for t in techniques_by_id.values() if t["id"] == rel["target_ref"]), None)
            if t:
                print(f"  - {get_name_and_id(t)}")

def display_software(identifier):
    obj = software_by_id.get(identifier.lower())
    if not obj:
        print(f"[!] Software not found: {identifier}")
        return
    print(f"\n=== SOFTWARE: {get_name_and_id(obj)} ===")
    print(f"Type: {obj.get('type').capitalize()}")
    print(f"Description:\n  {obj.get('description', '').strip()}")

def display_mitigation(identifier):
    obj = mitigations_by_id.get(identifier.lower())
    if not obj:
        print(f"[!] Mitigation not found: {identifier}")
        return
    print(f"\n=== MITIGATION: {get_name_and_id(obj)} ===")
    print(f"Description:\n  {obj.get('description', '').strip()}")

def display_tactic(identifier):
    key = identifier.lower()
    obj = tactics_by_id.get(key)

    if not obj:
        # Bütün taktikalarda id və external_id üzrə axtarış
        for tactic in tactics_by_id.values():
            if tactic.get("id", "").lower() == key or tactic.get("external_id", "").lower() == key or tactic.get("name", "").lower() == key:
                obj = tactic
                break

    if not obj:
        print(f"[!] Tactic not found: {identifier}")
        return

    print(f"\n=== TACTIC: {get_name_and_id(obj)} ===")
    print(f"Description:\n  {obj.get('description', '').strip()}")

def display_matrix(identifier):
    key = identifier.lower()
    obj = matrices_by_id.get(key)
    if not obj:
        # qısa uyğunluq yoxlaması
        for k, v in matrices_by_id.items():
            if key in k:
                obj = v
                break
    if not obj:
        print(f"[!] Matrix not found: {identifier}")
        return
    print(f"\n=== MATRIX: {obj.get('name')} ===")
    print(f"Tactics Included:")
    for tid in obj.get("tactic_refs", []):
        t = next((t for t in tactics_by_id.values() if t["id"] == tid), None)
        if t:
            print(f"  - {get_name_and_id(t)}")

def display_killchain(identifier):
    if identifier.lower() not in kc_phases:
        print(f"[!] Kill chain phase not found: {identifier}")
        return
    print(f"\n=== KILL CHAIN PHASE: {identifier} ===")
    print(f"Associated Techniques:")
    for t in techniques_by_id.values():
        for kcp in t.get("kill_chain_phases", []):
            if kcp["phase_name"].lower() == identifier.lower():
                print(f"  - {get_name_and_id(t)}")

def search(keyword):
    kw = keyword.lower()
    print(f"\n=== SEARCH RESULTS FOR: {keyword} ===")

    seen_ids = set()  # təkrarları aradan qaldırmaq üçün

    for db in [techniques_by_id, groups_by_id, software_by_id, mitigations_by_id, tactics_by_id, matrices_by_id, data_components_by_id]:
        for obj in db.values():
            # obyektin unikal id-si
            obj_id = obj.get("id") or get_ext_id(obj)
            if not obj_id:
                continue
            obj_id = obj_id.lower()

            # Əgər əvvəldən çap olunubsa, keç
            if obj_id in seen_ids:
                continue

            name = obj.get("name", "").lower()
            ext_id = get_ext_id(obj).lower()

            if kw in name or kw == ext_id:
                print(f"  - {get_name_and_id(obj)}")
                seen_ids.add(obj_id)

    for phase in kc_phases:
        if kw in phase:
            print(f"  - Kill Chain Phase: {phase}")


def display_all_techniques():
    for obj in sorted(techniques_by_id.values(), key=lambda x: x.get("name", "")):
        print(f"- {get_name_and_id(obj)}")

def display_all_groups():
    for obj in sorted(groups_by_id.values(), key=lambda x: x.get("name", "")):
        print(f"- {get_name_and_id(obj)}")

def display_all_software():
    for obj in sorted(software_by_id.values(), key=lambda x: x.get("name", "")):
        print(f"- {get_name_and_id(obj)}")

def display_all_mitigations():
    for obj in sorted(mitigations_by_id.values(), key=lambda x: x.get("name", "")):
        print(f"- {get_name_and_id(obj)}")

def display_all_tactics():
    # Taktikaları unikallaşdırmaq üçün set istifadə etmək olar
    unique = {}
    for obj in tactics_by_id.values():
        unique[obj["id"]] = obj
    for obj in sorted(unique.values(), key=lambda x: x.get("name", "")):
        print(f"- {get_name_and_id(obj)}")

def display_all_matrices():
    unique = {}
    for obj in matrices_by_id.values():
        unique[obj["name"]] = obj
    for obj in sorted(unique.values(), key=lambda x: x.get("name", "")):
        print(f"- {get_name_and_id(obj)}")

def display_all_killchains():
    for phase in sorted(kc_phases):
        print(f"- {phase}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("""
              
Usage:
              
  python mitre_enterprise_matrix.py <entity> <identifier>
  
  All <entity> --- technique, group, software, mitigation, tactic, matrix, killchain, search
  
  Look for specific tecnique   --- python mitre_enterprise_matrix.py technique T1059.001
  Look for specific group      --- python mitre_enterprise_matrix.py group APT29
  Look for specific software   --- python mitre_enterprise_matrix.py software cobaltstrike
  Look for specific mitigation --- python mitre_enterprise_matrix.py mitigation M1049
  Look for specific tactic     --- python mitre_enterprise_matrix.py tactic TA0002
  Look for specific matrix     --- python mitre_enterprise_matrix.py matrix enterprise
  Look for specific killchain  --- python mitre_enterprise_matrix.py killchain execution

  python mitre_enterprise_matrix.py search <keyword>
  
  Prints all as list --- python mitre_enterprise_matrix.py <entity> *
    !!! FOR "SEARCH" ENTITY, '*' IS NOT ALLOWED !!!
  
  Example:
    Prints all groups as list --- python mitre_enterprise_matrix.py group *
    usable for technique, group, software, mitigation, tactic, matrix, killchain
        """)
        sys.exit(1)

    cmd, val = sys.argv[1].lower(), sys.argv[2]

    if val == "*":
        if cmd == "technique":
            display_all_techniques()
        elif cmd == "group":
            display_all_groups()
        elif cmd == "software":
            display_all_software()
        elif cmd == "mitigation":
            display_all_mitigations()
        elif cmd == "tactic":
            display_all_tactics()
        elif cmd == "matrix":
            display_all_matrices()
        elif cmd == "killchain":
            display_all_killchains()
        else:
            print(f"[!] Unknown command: {cmd}")
    else:
        if cmd == "technique":
            display_technique(val)
        elif cmd == "group":
            display_group(val)
        elif cmd == "software":
            display_software(val)
        elif cmd == "mitigation":
            display_mitigation(val)
        elif cmd == "tactic":
            display_tactic(val)
        elif cmd == "matrix":
            display_matrix(val)
        elif cmd == "killchain":
            display_killchain(val)
        elif cmd == "search":
            search(val)
        else:
            print(f"[!] Unknown command: {cmd}")
