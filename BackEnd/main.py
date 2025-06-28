import os
import re
import random
import string
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Flask App Setup
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'dist'),
    static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'dist', 'assets')
)

# Configuration
app.config['SECRET_KEY'] = "c189ffd8d660e2c85caedfb6986dd2b4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "seidbayramovpb25@gmail.com"
app.config['MAIL_PASSWORD'] = "ykamyydefqthtbgz"
app.config['MAIL_DEFAULT_SENDER'] = "seidbayramovpb25@gmail.com"

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    is_verified = db.Column(db.Boolean, default=False)

# OTP Generator
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# ------------------ ROUTES ------------------ #

# Home Page (Dashboard)
@app.route('/')
def home():
    return render_template('dashboard/index.html')

# Register Form (GET)
@app.route('/register', methods=['GET'])
def register_form():
    return render_template('pages/register.html')  # Correct path

# Register (POST)
@app.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')

    pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(pattern, password):
        flash("Password must contain uppercase, digit, special char and be at least 8 chars.")
        return redirect(url_for('register_form'))

    if User.query.filter_by(email=email).first():
        flash("This email is already registered.")
        return redirect(url_for('register_form'))

    otp = generate_otp()
    session['otp'] = otp
    session['temp_user'] = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': generate_password_hash(password, method='pbkdf2:sha256')
    }

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
        flash("Email sending failed.")
        return redirect(url_for('register_form'))

    return redirect(url_for('verify'))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        input_otp = request.form.get('otp')
        if input_otp == session.get('otp'):
            temp_user = session.get('temp_user')
            if temp_user:
                user = User(
                    first_name=temp_user['first_name'],
                    last_name=temp_user['last_name'],
                    email=temp_user['email'],
                    password=temp_user['password'],
                    is_verified=True
                )
                db.session.add(user)
                db.session.commit()
                session.pop('otp', None)
                session.pop('temp_user', None)
                session['email'] = user.email
                flash("Registration successful!", "success")
                return redirect(url_for('home'))
        flash("Invalid OTP.", "danger")
    return render_template('pages/verify.html')


# Login (POST)
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
            session['temp_user'] = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'password': user.password
            }
            try:
                msg = Message(
                    subject='Your Login OTP Code',
                    recipients=[email],
                    body=f"Your login verification code is: {otp}"
                )
                mail.send(msg)
            except Exception as e:
                flash("Failed to send login OTP.")
                return redirect(url_for('register_form'))
            return redirect(url_for('verify'))
    flash("Invalid credentials.")
    return redirect(url_for('register_form'))

# Email Test Endpoint (Optional)
@app.route('/test-email')
def test_email():
    try:
        msg = Message(
            subject="Test Email",
            recipients=["seidbayramli2004@gmail.com"],
            body="Bu test emailidir."
        )
        mail.send(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# Static files
@app.route('/<path:filename>')
def serve_static(filename):
    full_path = os.path.join(app.template_folder, filename)
    if os.path.exists(full_path):
        return render_template(filename)
    return "Not Found", 404

# App Runner
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
