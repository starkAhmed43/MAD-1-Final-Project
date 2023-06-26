import os
from flask import Flask,request,render_template,redirect,url_for,make_response,jsonify,Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_restful import Resource, Api, marshal_with,fields
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from flask_security.models import fsqla_v2 as fsqla

from models import Tracker,Log,User
from __init__ import db
from __init__ import user_datastore
from helper_fns import JSONResponse,validateUserData,validateCardData,validateDeckData

views = Blueprint("views", __name__)

BASE = 'http://127.0.0.1:5000'




DASHBOARD_URL="/<string:username>/dashboard"

CREATE_DECK_URL="/<string:username>/deck/create"
VIEW_DECK_URL="/<string:username>/deck/<string:deckname>/view"
EDIT_DECK_URL="/<string:username>/deck/<string:deckname>/edit"
DELETE_DECK_URL="/<string:username>/deck/<string:deckname>/delete"

CREATE_CARD_URL="/<string:username>/deck/view/<string:deckname>/cards/create"
VIEW_CARD_URL="/<string:username>/deck/view/<string:deckname>/cards/<int:card_id>/view"
EDIT_CARD_URL="/<string:username>/deck/view/<string:deckname>/cards/<int:card_id>/edit"
DELETE_CARD_URL="/<string:username>/deck/view/<string:deckname>/cards/<int:card_id>/delete"

TEST_URL="/<string:username>/deck/<string:deckname>/test/<int:card_id>"





#-----------------------------------------------User------------------------------------------------------**
@views.route("/", methods=["POST","GET"])
def index():
    if request.method=="GET":
        return render_template("index.html")

    else:
        username=request.form.get("username")
        password=request.form.get("password")

        errors=validateUserData(username,password)
        if errors!={}:
            return render_template("user_error.html")

        user=Users.query.filter_by(username=username).first()
        if user == None:
            return render_template("user_error.html")
        if user.password != password:
            return render_template("user_error.html")
    return redirect(url_for("views.dashboard" ,username=user.username))     

@views.route("/user/create", methods=["POST","GET"])
def create_user():
    if request.method=="GET":
        return render_template("create_user.html")

    else:
        username=request.form.get("username")
        password=request.form.get("password")
        email=request.form.get("email")

        errors=validateUserData(username,password)
        if errors!={}:
            return render_template("create_user.html")

        duplicate_username=Users.query.filter_by(username=username).first()
        if duplicate_username!=None:
            return render_template("invalid_username.html")

        if not user_datastore.find_user(username=username):
            user_datastore.create_user(username=username, password=hash_password(password=password), email=email)

        #new_user=Users(username=username,password=password)
        #db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("views.index"))

@views.route("/resetpwd",methods=["POST","GET"])
def reset_pwd():
    if request.method=="GET":
        return render_template("reset_pwd.html")

    else:
        username=request.form.get("username")
        password=request.form.get("password")

        errors=validateUserData(username,password)
        if errors!={}:
            return render_template("reset_pwd.html")
        user=user.query.filter_by(username=username).first()
        if user == None:
            return render_template("user_error.html")
        else:
            user.password=password
            db.session.commit()
            return redirect(url_for("views.index"))

@views.route(DASHBOARD_URL,methods=["POST","GET"])
def dashboard(username):
    if request.method=="GET":
        user=user.query.filter_by(username=username).first()
        current_decks=Decks.query.filter_by(user_id=user.user_id).all()
        return render_template("dashboard.html",decks=current_decks,username=username)
#-----------------------------------------------User------------------------------------------------------**



#-----------------------------------------------Deck------------------------------------------------------**
@views.route(CREATE_DECK_URL,methods=["POST","GET"])
def create_deck(username):
    if request.method=="GET":
        return render_template("create_deck.html",username=username)

    else:
        deckname=request.form.get("deckname")
        errors=validateDeckData(username,deckname)
        if errors!={}:
            return redirect(url_for("views.create_deck",username=username))

        user=Users.query.filter_by(username=username).first()
        deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
        if deck != None:
            return render_template("deck_error.html",username=username)
        new_deck=Decks(deckname=deckname,user_id=user.user_id)
        db.session.add(new_deck)
        db.session.commit()
        return redirect(url_for("views.dashboard",username=username))

@views.route(DELETE_DECK_URL,methods=["GET","POST"])
def delete_deck(username,deckname):
    user=Users.query.filter_by(username=username).first()
    deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
    deck_cards=Cards.query.filter_by(deck_id=deck.deck_id).all()
    for card in deck_cards:
        db.session.delete(card)
    db.session.delete(deck)
    db.session.commit()
    return redirect(url_for("views.dashboard",username=username))

@views.route(EDIT_DECK_URL,methods=["GET","POST"])
def edit_deck(username,deckname):
    user=Users.query.filter_by(username=username).first()
    deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
    cards=Cards.query.filter_by(deck_id=deck.deck_id).all()
    if request.method=="GET":
        return render_template("edit_deck.html",username=username,deckname=deckname,cards=cards)
    else:
        new_deckname=request.form.get("deckname")
        errors=validateDeckData(username,new_deckname)
        if errors!={}:
            return redirect(url_for("views.edit_deck",username=username,deckname=deckname,cards=cards))

        deck.deckname=new_deckname
        db.session.commit()
        return redirect(url_for("views.dashboard",username=username))

@views.route(VIEW_DECK_URL)
def view_deck(username,deckname):
    user=Users.query.filter_by(username=username).first()
    deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
    cards=Cards.query.filter_by(deck_id=deck.deck_id).all()

    return render_template("view_deck.html",username=username,deckname=deckname,cards=cards)
#-----------------------------------------------Deck------------------------------------------------------**



#-----------------------------------------------Card------------------------------------------------------**
@views.route(CREATE_CARD_URL,methods=["POST","GET"])
def create_card(username,deckname):
    if request.method=="GET":
        return render_template("create_card.html",username=username,deckname=deckname)

    else:
        question=request.form.get("question")
        answer=request.form.get("answer")

        errors=validateCardData(question,answer)
        if errors!={}:
            return redirect(url_for("views.create_card",username=username,deckname=deckname))

        user=Users.query.filter_by(username=username).first()
        deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
        new_card=Cards(deck_id=deck.deck_id,question=question,answer=answer)

        db.session.add(new_card)
        db.session.commit()
        return redirect(url_for("views.edit_deck",username=username,deckname=deckname))

@views.route(VIEW_CARD_URL)
def view_card(username,deckname,card_id):
    card=Cards.query.filter_by(card_id=card_id).first()
    return render_template("view_card.html",username=username,card=card,deckname=deckname)

@views.route(DELETE_CARD_URL,methods=["GET","POST"])
def delete_card(username,deckname,card_id):
    card=Cards.query.filter_by(card_id=card_id).first()
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for("views.edit_deck",username=username,deckname=deckname))

@views.route(EDIT_CARD_URL,methods=["GET","POST"])
def edit_card(username,deckname,card_id):
    card=Cards.query.filter_by(card_id=card_id).first()
    if request.method=="GET":
        return render_template("edit_card.html",username=username,card=card,deckname=deckname)
    else:
        new_question=request.form.get("question")
        new_answer=request.form.get("answer")

        errors=validateCardData(new_question,new_answer)
        if errors!={}:
            return redirect(url_for("edit_card",username=username,card=card,deckname=deckname))
        card.question=new_question
        card.answer=new_answer
        db.session.commit()
        return redirect(url_for("views.edit_deck",username=username,deckname=deckname))
#-----------------------------------------------Card------------------------------------------------------**



#-----------------------------------------------Test------------------------------------------------------**
@views.route(TEST_URL,methods=["POST","GET"])
def test_helper(username,deckname,card_id):
    user=Users.query.filter_by(username=username).first()
    deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
    card=Cards.query.filter_by(card_id=card_id).first()

    last_reviewed=datetime.now()
    card.last_reviewed=last_reviewed.strftime("%c")
    deck.last_reviewed=last_reviewed.strftime("%c")
    
    if request.method=="GET":
        return render_template("view_test_card.html",username=username,deckname=deckname,card=card)
    else:
        answer=request.form.get("difficulty")
        score=0
        if answer != None:
            score_key={"Easy":3,"Medium":2,"Difficult":1}
            score=score_key[answer]
        card.last_score=score
        card.difficulty=answer
        update_deck_score(deck.deck_id)
        db.session.commit()
        return redirect(url_for("views.view_deck",username=username,deckname=deckname))


def update_deck_score(deck_id):
    cards=Cards.query.filter_by(deck_id=deck_id).all()
    total_score=0
    for card in cards:
        if card.last_score!=None:
            total_score+=card.last_score
    deck=Decks.query.filter_by(deck_id=deck_id).first()
    deck.total_score=total_score
#-----------------------------------------------Test------------------------------------------------------**