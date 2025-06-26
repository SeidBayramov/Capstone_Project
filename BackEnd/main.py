import os
import re
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from dotenv import load_dotenv

# .env faylını yüklə
load_dotenv()

# Flask tətbiqi
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'dist'),
    static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'dist', 'assets')
)

# Konfiqurasiya
app.config['SECRET_KEY'] = os.getenv("c189ffd8d660e2c85caedfb6986dd2b4", "fallback_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("seidbayramovpb25@gmal.com")
app.config['MAIL_PASSWORD'] = os.getenv("womuifmsniznktyn")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("seidbayramov25@gmail.com")

# Extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    is_verified = db.Column(db.Boolean, default=False)

# OTP generator
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# Ana səhifə
@app.route('/')
def home():
    return render_template('dashboard/index.html')

# Register (GET)
@app.route('/register', methods=['GET'])
def register_form():
    return render_template('auth-pages/register.html')

# Register (POST)
@app.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')

     # Parol gücünü yoxla
    password_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(password_pattern, password):
        return "Password must be at least 8 characters long, include 1 uppercase letter, 1 number, and 1 special character."


    # Mövcud istifadəçini yoxla
    if User.query.filter_by(email=email).first():
        return "This email is already registered. Please login or use another email."

    # Yeni istifadəçi
    user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    # OTP yarat
    otp = generate_otp()
    session['email'] = email
    session['otp'] = otp

    # OTP emaili göndər
    msg = Message(
        subject='Your Verification Code',
        recipients=[email],
        body=f"Your OTP code is: {otp}"
        # sender avtomatik olaraq config-dən götürüləcək
    )
    mail.send(msg)

    return redirect(url_for('verify'))

# Verify OTP
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        input_otp = request.form.get('otp')
        if input_otp == session.get('otp'):
            user = User.query.filter_by(email=session.get('email')).first()
            if user:
                user.is_verified = True
                db.session.commit()
                return redirect(url_for('home'))
        return "Invalid OTP. Try again."
    return render_template('auth-pages/verify.html')

# Statik fayllar
@app.route('/<path:filename>')
def serve_any_page(filename):
    full_path = os.path.join(app.template_folder, filename)
    if os.path.exists(full_path):
        return render_template(filename)
    return "Not Found", 404

# DB yarat və serveri başlat
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
