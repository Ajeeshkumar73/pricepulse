import os
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
import io
import base64
import hashlib
from PIL import Image
from pyzbar.pyzbar import decode

# -------------------------------
# App Setup
# -------------------------------
app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SESSION_SECRET") or "supersecretkey"

# MongoDB
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/campus_wallet")
mongo = PyMongo(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# -------------------------------
# User Class
# -------------------------------
class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.username = user_doc["username"]
        self.email = user_doc["email"]
        self.role = user_doc.get("role", "student")

    @staticmethod
    def get(user_id):
        user_doc = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User(user_doc) if user_doc else None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form.get('phone', '')
        role = request.form.get('role', 'student')

        if mongo.db.users.find_one({"email": email}):
            flash('Email already registered!', 'error')
            return render_template('register.html')
        if mongo.db.users.find_one({"username": username}):
            flash('Username already taken!', 'error')
            return render_template('register.html')

        user_id = mongo.db.users.insert_one({
            "email": email,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "role": role,
            "password": generate_password_hash(password),
            "created_at": datetime.utcnow()
        }).inserted_id

        # Create wallet
        mongo.db.wallets.insert_one({
            "user_id": str(user_id),
            "balance": 0,
            "updated_at": datetime.utcnow()
        })

        # Vendor profile
        if role == 'vendor':
            shop_name = request.form.get('shop_name', '')
            shop_type = request.form.get('shop_type', 'canteen')
            mongo.db.vendors.insert_one({
                "user_id": str(user_id),
                "shop_name": shop_name,
                "shop_type": shop_type,
                "active": True
            })

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_doc = mongo.db.users.find_one({"username": username})
        if user_doc and check_password_hash(user_doc["password"], password):
            login_user(User(user_doc))
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        wallet = mongo.db.wallets.find_one({"user_id": current_user.id})
        transactions = list(mongo.db.transactions.find({
            "$or": [{"sender_id": current_user.id}, {"receiver_id": current_user.id}]
        }).sort("created_at", -1).limit(10))
        return render_template('student_dashboard.html', wallet=wallet, transactions=transactions)

    elif current_user.role == 'vendor':
        vendor = mongo.db.vendors.find_one({"user_id": current_user.id})
        recent_payments = list(mongo.db.transactions.find({"receiver_id": current_user.id}).sort("created_at", -1).limit(10))
        return render_template('vendor_dashboard.html', vendor=vendor, recent_payments=recent_payments)

    elif current_user.role == 'admin':
        total_users = mongo.db.users.count_documents({})
        total_transactions = mongo.db.transactions.count_documents({})
        total_wallet_balance = sum([w.get("balance", 0) for w in mongo.db.wallets.find()])
        return render_template('admin_dashboard.html',
                               total_users=total_users,
                               total_transactions=total_transactions,
                               total_wallet_balance=total_wallet_balance)

    return redirect(url_for('login'))


@app.route('/load_money', methods=['GET', 'POST'])
@login_required
def load_money():
    if current_user.role != 'student':
        flash('Only students can load money!', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        amount = float(request.form['amount'])
        if amount <= 0:
            flash('Enter a valid amount!', 'error')
            return render_template('load_money.html')

        wallet = mongo.db.wallets.find_one({"user_id": current_user.id})
        new_balance = wallet["balance"] + amount if wallet else amount
        mongo.db.wallets.update_one(
            {"user_id": current_user.id},
            {"$set": {"balance": new_balance, "updated_at": datetime.utcnow()}},
            upsert=True
        )
        mongo.db.transactions.insert_one({
            "transaction_id": str(uuid.uuid4()),
            "sender_id": current_user.id,
            "receiver_id": current_user.id,
            "amount": amount,
            "transaction_type": "load_money",
            "description": "Money loaded into wallet",
            "created_at": datetime.utcnow()
        })
        flash(f'₹{amount} loaded successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('load_money.html')


@app.route('/generate_qr')
@login_required
def generate_qr():
    if current_user.role != 'vendor':
        flash('Only vendors can generate QR codes!', 'error')
        return redirect(url_for('dashboard'))

    vendor = mongo.db.vendors.find_one({"user_id": current_user.id})
    if not vendor:
        flash('Vendor profile not found!', 'error')
        return redirect(url_for('dashboard'))

    expires_at = datetime.utcnow() + timedelta(hours=24)
    qr_token = str(uuid.uuid4())
    qr_payload = f"vendor_id:{vendor['_id']}|user_id:{current_user.id}|token:{qr_token}|expires:{expires_at.isoformat()}"
    signature = hashlib.sha256(f"{qr_payload}{app.secret_key}".encode()).hexdigest()[:16]
    qr_data = f"{qr_payload}|sig:{signature}"

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_base64 = base64.b64encode(img_io.getvalue()).decode()

    mongo.db.qrcodes.insert_one({
        "vendor_id": str(vendor["_id"]),
        "qr_data": qr_token,
        "expires_at": expires_at,
        "is_active": True
    })

    return render_template('qr_code.html', qr_image=img_base64, vendor=vendor)


@app.route('/scan_payment', methods=['GET', 'POST'])
@login_required
def scan_payment():
    if current_user.role != 'student':
        flash('Only students can pay!', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if 'qr_file' not in request.files:
            flash('No QR file uploaded!', 'error')
            return render_template('scan_payment.html')
        file = request.files['qr_file']
        if not file:
            flash('No QR file selected!', 'error')
            return render_template('scan_payment.html')

        amount = float(request.form['amount'])

        # Decode QR
        try:
            img = Image.open(file)
            decoded = decode(img)
            if not decoded:
                flash('Could not read QR!', 'error')
                return render_template('scan_payment.html')
            qr_data = decoded[0].data.decode('utf-8')
        except Exception:
            flash('Invalid QR image!', 'error')
            return render_template('scan_payment.html')

        # ----------------
        # Validate QR content
        # ----------------
        try:
            qr_parts = qr_data.split('|')
            vendor_id = qr_parts[0].split(':')[1]
            vendor_user_id = qr_parts[1].split(':')[1]
            qr_token = qr_parts[2].split(':')[1]
            expires_str = qr_parts[3].split(':')[1]
            signature = qr_parts[4].split(':')[1]

            expires_at = datetime.fromisoformat(expires_str)
            if datetime.utcnow() > expires_at:
                flash('QR expired!', 'error')
                return render_template('scan_payment.html')

            expected_signature = hashlib.sha256(f"{'|'.join(qr_parts[:4])}{app.secret_key}".encode()).hexdigest()[:16]
            if signature != expected_signature:
                flash('Invalid QR signature!', 'error')
                return render_template('scan_payment.html')

            qr_record = mongo.db.qrcodes.find_one({"vendor_id": vendor_id, "qr_data": qr_token, "is_active": True})
            if not qr_record:
                flash('Inactive QR code!', 'error')
                return render_template('scan_payment.html')

        except Exception:
            flash('Invalid QR format!', 'error')
            return render_template('scan_payment.html')

        vendor = mongo.db.vendors.find_one({"_id": ObjectId(vendor_id), "user_id": vendor_user_id})
        if not vendor or not vendor.get("active", True):
            flash('Vendor inactive!', 'error')
            return render_template('scan_payment.html')

        student_wallet = mongo.db.wallets.find_one({"user_id": current_user.id})
        if not student_wallet or student_wallet["balance"] < amount:
            flash('Insufficient balance!', 'error')
            return render_template('scan_payment.html')

        vendor_wallet = mongo.db.wallets.find_one({"user_id": vendor_user_id})
        vendor_balance = vendor_wallet["balance"] if vendor_wallet else 0

        # Update balances
        mongo.db.wallets.update_one(
            {"user_id": current_user.id},
            {"$set": {"balance": student_wallet["balance"] - amount, "updated_at": datetime.utcnow()}}
        )
        mongo.db.wallets.update_one(
            {"user_id": vendor_user_id},
            {"$set": {"balance": vendor_balance + amount, "updated_at": datetime.utcnow()}},
            upsert=True
        )

        # Record transaction
        mongo.db.transactions.insert_one({
            "transaction_id": str(uuid.uuid4()),
            "sender_id": current_user.id,
            "receiver_id": vendor_user_id,
            "amount": amount,
            "transaction_type": "payment",
            "description": f'Payment to {vendor["shop_name"]} ({vendor["shop_type"]})',
            "created_at": datetime.utcnow()
        })

        flash(f'Payment of ₹{amount} successful!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('scan_payment.html')


@app.route('/transactions')
@login_required
def transactions():
    if current_user.role == 'student':
        user_transactions = list(mongo.db.transactions.find({
            "$or": [{"sender_id": current_user.id}, {"receiver_id": current_user.id}]
        }).sort("created_at", -1))
    elif current_user.role == 'vendor':
        user_transactions = list(mongo.db.transactions.find({"receiver_id": current_user.id}).sort("created_at", -1))
    else:
        user_transactions = list(mongo.db.transactions.find().sort("created_at", -1))
    return render_template('transactions.html', transactions=user_transactions)


# -------------------------------
# Run
# -------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
