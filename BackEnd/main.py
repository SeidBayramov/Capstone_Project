import os
import re
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# External fetcher
from news_fetcher11 import fetch_news

# Flask Setup
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'dist'),
    static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'dist', 'assets')
)

# Config
app.config['SECRET_KEY'] = "c189ffd8d660e2c85caedfb6986dd2b4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "seidbayramovpb25@gmail.com"
app.config['MAIL_PASSWORD'] = "ykamyydefqthtbgz"
app.config['MAIL_DEFAULT_SENDER'] = "seidbayramovpb25@gmail.com"

# Initialize
db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# OTP Generator
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

# Send OTP Email
def send_otp_email(to_email, otp):
    try:
        msg = Message(subject='Your OTP Code', recipients=[to_email], body=f"Your OTP is: {otp}")
        mail.send(msg)
        print(f"[INFO] OTP {otp} sent to {to_email}")
    except Exception as e:
        print("[ERROR] Email error:", str(e))
        flash("OTP email could not be sent.")

# ------------------ ROUTES ------------------ #

@app.route('/')
@login_required
def home():
    return render_template('pages/login-v1.html')

# ------------------ REGISTER ------------------ #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(pattern, password):
            flash("Password must contain uppercase, digit, special char and be at least 8 chars.")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("This email is already registered.")
            return redirect(url_for('register'))

        otp = generate_otp()
        session['otp'] = otp
        session['pending_register_user_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': generate_password_hash(password, method='pbkdf2:sha256')
        }

        send_otp_email(email, otp)
        return redirect('/verify')

    return render_template('pages/register.html')

# ------------------ VERIFY ------------------ #
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if entered_otp != session.get('otp'):
            flash('Incorrect OTP. Please try again.', 'danger')
            return redirect('/verify')
        if 'pending_register_user_data' in session:
            user_data = session.pop('pending_register_user_data')
            user = User(**user_data, is_verified=True)
            db.session.add(user)
            db.session.commit()
            flash('Registration complete. Please login.', 'success')
            return redirect('/login')
        elif 'pending_login_user_id' in session:
            user_id = session.pop('pending_login_user_id')
            user = User.query.get(user_id)
            login_user(user)
            flash('Login successful!', 'success')
            return redirect('/dashboard/index.html')

    return render_template('pages/verify.html')

# ------------------ LOGIN ------------------ #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", 'danger')
            return redirect('/login')

        otp = generate_otp()
        session['otp'] = otp
        session['pending_login_user_id'] = user.id
        send_otp_email(user.email, otp)
        return redirect('/verify')

    return render_template('pages/login-v1.html')

# ------------------ LOGOUT ------------------ #
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect('/login')

# ------------------ API: News ------------------ #
@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        news = fetch_news()
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ STATIC FALLBACK ------------------ #
@app.route('/<path:filename>')
def serve_static(filename):
    full_path = os.path.join(app.template_folder, filename)
    if os.path.exists(full_path):
        return render_template(filename)
    return "Not Found", 404

# ------------------ RUN ------------------ #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
