from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String)
    accounts = relationship("Account", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    is_admin = Column(Boolean, default=False)

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    balance = Column(Numeric, default=0)
    user = relationship("User", back_populates="accounts")

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True)
    amount = Column(Numeric)
    account_id = Column(Integer, ForeignKey('accounts.id', ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    account = relationship("Account")
    user = relationship("User", back_populates="payments")
