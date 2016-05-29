from sqlalchemy import (Column, Integer, String,
                        DateTime, Boolean)
from database import Base
from werkzeug.security import generate_password_hash


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True)
    email = Column(String(40), unique=True)
    password = Column(String)

    def __init__(self, form):
        self.username = form.username.data
        self.email = form.email.data
        self.password = generate_password_hash(form.password.data)


class Player(Base):
    __tablename__ = 'player'
    user_id = Column(Integer, primary_key=True)
    nickname = Column(String(40))
    gold = Column(Integer, default=100)
    diamond = Column(Integer, default=0)
    chance = Column(Integer, default=20)


class Gossip(Base):
    __tablename__ = 'gossip'
    gossip_id = Column(Integer, primary_key=True)
    content = Column(Integer, nullable=False)
    price = Column(Integer)
    datetime = Column(DateTime)
    user_id = Column(Integer)

    def __init__(self, form):
        self.content = form['content']
        self.price = form['price']
        self.datetime = form['datetime']
        self.user_id = form['user_id']


class Friend(Base):
    __tablename__ = 'friend'
    record_id = Column(Integer, primary_key=True)
    user1 = Column(Integer)
    user2 = Column(Integer)
    watch = Column(Boolean, default=False)


class Invite(Base):
    __tablename__ = 'invite'
    record_id = Column(Integer, primary_key=True)
    user1 = Column(Integer)
    user2 = Column(Integer)
