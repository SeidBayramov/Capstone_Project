import os
import re
import random
import string
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Flask tətbiqi
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'dist'),
    static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'dist', 'assets')
)

# Birbaşa konfiqurasiya (dotenv olmadan)
app.config['SECRET_KEY'] = "c189ffd8d660e2c85caedfb6986dd2b4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "seidbayramovpb25@gmail.com"
app.config['MAIL_PASSWORD'] = "ykamyydefqthtbgz"
app.config['MAIL_DEFAULT_SENDER'] = "seidbayramovpb25@gmail.com"

# Extensions
db = SQLAlchemy(app)
mail = Mail()
mail.init_app(app)

# User modeli
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

# Qeydiyyat formu (GET)
@app.route('/register', methods=['GET'])
def register_form():
    return render_template('auth-pages/register.html')

# Qeydiyyat (POST)
@app.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')

    # Parol gücünü yoxla
    pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(pattern, password):
        flash("Password must contain uppercase, digit, special char and be at least 8 chars.", "danger")
        return redirect(url_for('register_form'))

    if User.query.filter_by(email=email).first():
        flash("This email is already registered.", "warning")
        return redirect(url_for('register_form'))

    hashed_password = generate_password_hash(password)
    user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()

    otp = generate_otp()
    session['email'] = email
    session['otp'] = otp

    # Email göndər
    try:
        msg = Message(
            subject='Your Verification Code',
            recipients=[email],
            body=f"Your OTP code is: {otp}"
        )
        mail.send(msg)
        print(f"[INFO] OTP {otp} sent to {email}")
    except Exception as e:
        print("[ERROR] Email error:", str(e))
        flash("Email sending failed. Try again.", "danger")
        return redirect(url_for('register_form'))

    return redirect(url_for('verify'))

# OTP Doğrulama
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        input_otp = request.form.get('otp')
        if input_otp == session.get('otp'):
            user = User.query.filter_by(email=session.get('email')).first()
            if user:
                user.is_verified = True
                db.session.commit()
                session.pop('otp', None)
                return redirect(url_for('home'))
        flash("Invalid OTP.", "danger")
    return render_template('auth-pages/verify.html')

# Test email
@app.route('/test-email')
def test_email():
    try:
        msg = Message(
            subject="Test Email",
            recipients=["seidbayramli2004@gmail.com"],
            body="Bu test emailidir."
        )
        mail.send(msg)
        return "Email uğurla göndərildi!"
    except Exception as e:
        return f"Email göndərilmədi: {str(e)}"

# Giriş
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        if user.is_verified:
            session['email'] = user.email
            return redirect(url_for('home'))
        else:
            otp = generate_otp()
            session['otp'] = otp
            try:
                msg = Message(
                    subject='Your Login OTP Code',
                    recipients=[email],
                    body=f"Your login verification code is: {otp}"
                )
                mail.send(msg)
                print(f"[INFO] Login OTP {otp} sent to {email}")
            except Exception as e:
                print("[ERROR] Login OTP email failed:", str(e))
                flash("Could not send login OTP.", "danger")
                return redirect(url_for('login'))
            return redirect(url_for('verify'))
    else:
        flash("Invalid credentials.", "danger")
        return redirect(url_for('login'))

# Statik fayllar
@app.route('/<path:filename>')
def serve_static(filename):
    full_path = os.path.join(app.template_folder, filename)
    if os.path.exists(full_path):
        return render_template(filename)
    return "Not Found", 404

# App işlədilir
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
