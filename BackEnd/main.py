import os
import re
import random
import string
from datetime import datetime, timedelta
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

# Konfiqurasiya (dotenv olmadan birbaşa dəyərlər)
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

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/')
def home():
    return 'Home Page - Welcome!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password, first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        db.session.commit()

        otp = generate_otp()
        session['email'] = email
        session['otp'] = otp
        session['otp_expires_at'] = (datetime.utcnow() + timedelta(minutes=1)).isoformat()

        try:
            msg = Message('Your OTP Code', recipients=[email])
            msg.body = f"Your OTP code is: {otp}"
            msg.html = f"""
                <h2>ShadowLink OTP</h2>
                <p>Your verification code is:</p>
                <div style='font-size:24px; font-weight:bold; color:#27ae60;'>{otp}</div>
                <p>This code will expire in 1 minute.</p>
            """
            mail.send(msg)
        except Exception as e:
            print("Email send error:", str(e))
            flash("Error sending email.", "danger")

        return redirect(url_for('verify'))

    return render_template('auth-pages/register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        input_otp = request.form.get('otp')
        otp = session.get('otp')
        expires_at = session.get('otp_expires_at')

        if not otp or not expires_at or datetime.utcnow() > datetime.fromisoformat(expires_at):
            flash("OTP expired. Please request a new one.", "warning")
            return redirect(url_for('resend_otp'))

        if input_otp == otp:
            user = User.query.filter_by(email=session.get('email')).first()
            if user:
                user.is_verified = True
                db.session.commit()
                session.pop('otp', None)
                session.pop('otp_expires_at', None)
                return redirect(url_for('home'))
        else:
            flash("Invalid OTP.", "danger")

    return render_template('auth-pages/verify.html')

@app.route('/resend-otp')
def resend_otp():
    email = session.get('email')
    if not email:
        flash("Session expired. Please register again.", "warning")
        return redirect(url_for('register'))

    otp = generate_otp()
    session['otp'] = otp
    session['otp_expires_at'] = (datetime.utcnow() + timedelta(minutes=1)).isoformat()

    try:
        msg = Message('Resent OTP Code', recipients=[email])
        msg.body = f"Your new OTP code is: {otp}"
        msg.html = f"""
            <h2>ShadowLink OTP Resent</h2>
            <p>Your new verification code is:</p>
            <div style='font-size:24px; font-weight:bold; color:#27ae60;'>{otp}</div>
            <p>This code will expire in 1 minute.</p>
        """
        mail.send(msg)
        flash("New OTP code sent!", "success")
    except Exception as e:
        print("Resend email error:", str(e))
        flash("Failed to resend OTP. Try again later.", "danger")

    return redirect(url_for('verify'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
