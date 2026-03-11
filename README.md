# 🏢 Price Pulse: Campus Wallet System

![Campus Wallet Hero](campus_wallet_hero.png)

Price Pulse is a cutting-edge **Campus Wallet System** designed to simplify and digitize financial transactions within educational environments. From student cafeterias to campus bookstores, Price Pulse provides a seamless, secure, and efficient way for students to pay and vendors to receive payments using QR code technology.

---

## ✨ Key Features

### 🎓 For Students
- **Digital Wallet**: Securely store and manage your campus funds.
- **Easy Loading**: Load money into your wallet with a few clicks.
- **QR Code Payments**: Make instant payments by scanning vendor QR codes.
- **Transaction History**: Track every rupee spent with detailed transaction logs.

### 🏪 For Vendors
- **Dynamic QR Generation**: Generate unique, secure QR codes for processing payments.
- **Real-time Payment Tracking**: Receive instant notifications and view recent payments on your dashboard.
- **Vendor Dashboard**: Monitor shop earnings and manage your vendor profile.

### 🛡️ For Administrators
- **System-wide Overview**: Monitor total users, transactions, and overall wallet balance.
- **User Management**: Gain insights into student and vendor activities.
- **Financial Audit**: Maintain a complete audit trail of all campus transactions.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | [Flask](https://flask.palletsprojects.com/) |
| **Database** | [MongoDB](https://www.mongodb.com/) (PyMongo) |
| **Authentication** | [Flask-Login](https://flask-login.readthedocs.io/) |
| **Styling** | [Bootstrap 5](https://getbootstrap.com/) |
| **Icons** | [Font Awesome 6](https://fontawesome.com/) |
| **QR Engine** | [qrcode-python](https://github.com/lincolnloop/python-qrcode), [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB installed and running locally
- Windows OS (referenced by the environment)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ajeeshkumar73/pricepulse.git
   cd pricepulse
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file or set the following environment variables:
   ```env
   SESSION_SECRET=your_super_secret_key
   MONGO_URI=mongodb://localhost:27017/campus_wallet
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```
   The application will be available at `http://127.0.0.1:5000`.

---

## 📂 Project Structure

- `main.py`: Core application logic, routes, and MongoDB interactions.
- `models.py`: (Legacy) SQLAlchemy models.
- `templates/`: Jinja2 HTML templates for the UI.
- `requirements.txt`: Python package dependencies.
- `replit.md`: System architecture and overview.

---

## 🔒 Security
- **Password Hashing**: Securely hashed using `Werkzeug Security`.
- **Signed QR Codes**: QR codes are digitally signed with a SHA-256 HMAC using the app's secret key to prevent tampering.
- **Role-based Access**: Users are restricted to their specific dashboard and actions based on their role (Student, Vendor, Admin).

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
