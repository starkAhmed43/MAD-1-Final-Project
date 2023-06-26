from __init__ import db
from flask_sqlalchemy import SQLAlchemy


class Users(db.Model):
    __tablename__="Users"
    user_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    user_IDS=db.relationship("Decks",backref="Users")

class Decks(db.Model):
    __tablename__="Decks"
    deck_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    deckname=db.Column(db.String,unique=True,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("Users.user_id"))
    last_reviewed=db.Column(db.String)
    total_score=db.Column(db.Integer)
    cards=db.relationship("Cards",backref="Decks")

class Cards(db.Model):
    __tablename__="Cards"
    card_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    deck_id=db.Column(db.Integer,db.ForeignKey("Decks.deck_id"),nullable=False)
    question=db.Column(db.String,nullable=False)
    difficulty=db.Column(db.String,nullable=False)
    answer=db.Column(db.String,nullable=False)
    last_reviewed=db.Column(db.String)
    last_score=db.Column(db.Integer)