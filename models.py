import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(120), unique=True, nullable=False)
    username = mapped_column(String(80), unique=True, nullable=False)
    password_hash = mapped_column(String(255), nullable=False)
    first_name = mapped_column(String(50), nullable=False)
    last_name = mapped_column(String(50), nullable=False)
    phone = mapped_column(String(15), nullable=True)
    role = mapped_column(String(20), nullable=False, default='student')  # student, vendor, admin
    active = mapped_column(Boolean, default=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    transactions_sent = relationship("Transaction", foreign_keys="Transaction.sender_id", back_populates="sender")
    transactions_received = relationship("Transaction", foreign_keys="Transaction.receiver_id", back_populates="receiver")
    vendor_profile = relationship("Vendor", back_populates="user", uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Wallet(db.Model):
    __tablename__ = 'wallets'
    
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    balance = mapped_column(Float, default=0.0, nullable=False)
    active = mapped_column(Boolean, default=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    
    def __repr__(self):
        return f'<Wallet {self.user.username}: {self.balance}>'


class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    shop_name = mapped_column(String(100), nullable=False)
    shop_type = mapped_column(String(50), nullable=False)  # canteen, library, stationery
    description = mapped_column(Text, nullable=True)
    active = mapped_column(Boolean, default=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="vendor_profile")
    
    def __repr__(self):
        return f'<Vendor {self.shop_name}>'


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = mapped_column(Integer, primary_key=True)
    transaction_id = mapped_column(String(100), unique=True, nullable=False)
    sender_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    amount = mapped_column(Float, nullable=False)
    transaction_type = mapped_column(String(20), nullable=False)  # payment, load_money, refund
    description = mapped_column(String(255), nullable=True)
    status = mapped_column(String(20), default='completed')  # pending, completed, failed
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="transactions_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="transactions_received")
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id}: {self.amount}>'


class QRCode(db.Model):
    __tablename__ = 'qrcodes'
    
    id = mapped_column(Integer, primary_key=True)
    vendor_id = mapped_column(Integer, ForeignKey('vendors.id'), nullable=False)
    qr_data = mapped_column(Text, nullable=False)
    amount = mapped_column(Float, nullable=True)  # For fixed amount QR codes
    active = mapped_column(Boolean, default=True)
    expires_at = mapped_column(DateTime, nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QRCode {self.id} for Vendor {self.vendor_id}>'