import subprocess
import os

def run_sherlock(username):
    sherlock_path = os.path.join(os.path.dirname(__file__), 'sherlock', 'sherlock_project', 'sherlock.py')

    try:
        result = subprocess.run(
            ['python', sherlock_path, username, '--print-found', '--no-color'],
            capture_output=True, text=True, timeout=180
        )
        output = result.stdout
        return output if output else "No accounts found."
    except subprocess.TimeoutExpired:
        return "❌ Timeout: Sherlock scan took too long."
    except Exception as e:
        return f"❌ Error running Sherlock: {str(e)}"
