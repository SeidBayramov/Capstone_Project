from flask import Flask, render_template
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'dist', ''),  # HTML-lər burdadır
    static_folder=os.path.join(BASE_DIR, 'dist', 'assets')  # JS, CSS, şəkillər
)

@app.route('/')
def home():
    return render_template('dashboard/index.html')

@app.route('/<path:filename>')
def serve_any_page(filename):
    full_path = os.path.join(app.template_folder, filename)
    print("Looking for:", full_path)
    print("Exists?", os.path.exists(full_path))
    if os.path.exists(full_path):
        return render_template(filename)
    return "Not Found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
