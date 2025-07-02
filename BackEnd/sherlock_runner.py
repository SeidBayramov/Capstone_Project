import subprocess
import os
import re

def run_sherlock(username):
    sherlock_path = os.path.join(os.path.dirname(__file__), 'sherlock', 'sherlock_project', 'sherlock.py')
    output_file = f"{username}.txt"

    try:
        result = subprocess.run(
            ['python', sherlock_path, username, '--print-found', '--no-color'],
            capture_output=True, text=True, timeout=180
        )
        output = result.stdout

        # Fayldan oxu əgər stdout boşdursa
        if not output and os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                output = f.read()

        # Rəng kodlarını təmizlə
        output = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)

        return output.strip() if output else "No accounts found."

    except subprocess.TimeoutExpired:
        return "❌ Timeout: Sherlock scan took too long."
    except Exception as e:
        return f"❌ Error running Sherlock: {str(e)}"
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)
