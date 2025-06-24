from flask import Flask, render_template
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'dist'),
    static_folder=os.path.join(BASE_DIR, 'dist', 'assets')
)

@app.route('/')
def home():
    index_path = os.path.join(app.template_folder, 'index.html')
    print("Looking for:", index_path)
    print("Exists?", os.path.exists(index_path))  # Bu hissə faylın həqiqətən olub olmadığını yoxlayır
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
