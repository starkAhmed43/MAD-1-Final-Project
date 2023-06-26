from flask import Flask,request,render_template,redirect,url_for,make_response,jsonify,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_restful import Resource, Api, marshal_with,fields

from models import Users,Decks,Cards
from __init__ import db
from flask import current_app as app
from helper_fns import JSONResponse,validateUserData,validateCardData,validateDeckData





class DeckAPI(Resource):
    def DECK_TEMPLATE(deck,error_code):
        value={
            "deck_id":deck.deck_id,
            "user_id":deck.user_id,
            "deckname":deck.deckname,
            "last_reviewed":deck.last_reviewed,
            "last_score":deck.total_score
        }
        return JSONResponse(value,error_code)

    def POST_DECK_TEMPLATE(deck,error_code):
        value={
            "deck_id":deck.deck_id,
            "user_id":deck.user_id,
            "deckname":deck.deckname
        }
        return JSONResponse(value,error_code)

    def get(self,username,deckname):
        try:
            user=Users.query.filter_by(username=username).first()
            deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
            if deck==None: #if the deck doesn't exist
                return JSONResponse("Deck not found.",404)
            return DeckAPI.DECK_TEMPLATE(deck,200)
        except:
            return JSONResponse("Internal Server Error",500)

    def put(self,username,deckname):
        new_deckname=request.form.get("new_deckname")

        errors=validateDeckData(username,new_deckname)
        if errors!={}: #if any errors are thrown, return them
            return JSONResponse(errors,400)
            
        try:
            user=Users.query.filter_by(username=username).first()
            deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()

            if deck==None: #if the deck doesn't exist
                return JSONResponse("Deck not found.",404)  #return "NOT FOUND - 404"

            deck.deckname=new_deckname
            db.session.commit()
            updated_deck=Decks.query.filter_by(deck_id=deck.deck_id).first()
            return DeckAPI.POST_DECK_TEMPLATE(updated_deck,200)
        except:
            return JSONResponse("Internal Server Error.",500)

    def post(self):
        username=request.form.get("username")
        deckname=request.form.get("deckname")

        errors=validateDeckData(username,deckname)
        if errors!={}: #if any errors are thrown, return them
            return JSONResponse(errors,400)

        try:
            user=Users.query.filter_by(username=username).first()
            duplicate_deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
            if duplicate_deck != None: #if duplicates exist, return 409
                return JSONResponse("Deck already exists for user",409)

            new_deck=Decks(deckname=deckname,user_id=user.user_id)
            db.session.add(new_deck)
            db.session.commit()

            deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
            return DeckAPI.POST_DECK_TEMPLATE(deck,201)
        except:
            return JSONResponse("Internal Server Error.",500)

    def delete(self,username,deckname):
        try:
            user=Users.query.filter_by(username=username).first()
            deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()

            if deck==None: #if the deck doesn't exist
                return JSONResponse("Deck not found",404)

            deck_cards=Cards.query.filter_by(deck_id=deck.deck_id).all()
            for card in deck_cards:
                db.session.delete(card)
            db.session.delete(deck)
            db.session.commit()
            return JSONResponse("Deck successfully deleted.",200)
        except:
            return JSONResponse("Internal Server Error.",500)






class CardAPI(Resource):
    def CARD_TEMPLATE(card,deck,user,error_code):
        value={
            "username":user.username,
            "deckname":deck.deckname,
            "card_id":card.card_id,
            "question":card.question,
            "answer":card.answer,
            "difficulty":card.difficulty,
            "last_reviewed":card.last_reviewed,
            "last_score":card.last_score
        }
        return JSONResponse(value,error_code)

    def POST_CARD_TEMPLATE(card,deck,user,error_code):
        value={
            "username":user.username,
            "deckname":deck.deckname,
            "card_id":card.card_id,
            "deck_id":card.deck_id,
            "question":card.question,
            "answer":card.answer,
        }
        return JSONResponse(value,error_code)

    def post(self):
        username=request.form.get("username")
        deckname=request.form.get("deckname")
        question=request.form.get("question")
        answer=request.form.get("answer")

        errors=validateCardData(question,answer)
        if errors!={}:
            return JSONResponse(errors,400)

        try:

            user=Users.query.filter_by(username=username).first()
            if user==None:
                return JSONResponse("User not found",404)

            deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
            if deck==None:
                return JSONResponse("Deck not found",404)

            duplicate_card=Cards.query.filter_by(deck_id=deck.deck_id,question=question,answer=answer).first()
            if duplicate_card != None: #if duplicates exist, return 409
                return JSONResponse("Card already exists for user",409)

            new_card=Cards(deck_id=deck.deck_id,question=question,answer=answer)
            db.session.add(new_card)
            db.session.commit()

            card=Cards.query.filter_by(deck_id=deck.deck_id,question=question,answer=answer).first()
            return CardAPI.POST_CARD_TEMPLATE(card,deck,user,201)
        except:
            return JSONResponse("Internal Server Error",500)

    def get(self,username,deckname,card_id):
        try:
            user=Users.query.filter_by(username=username).first()
            if user==None:
                return JSONResponse("User not found",404)

            deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
            if deck==None:
                return JSONResponse("Deck not found",404)

            card=Cards.query.filter_by(card_id=card_id,deck_id=deck.deck_id).first()
            if card==None:
                return JSONResponse("Card not found",404)

            return CardAPI.CARD_TEMPLATE(card,deck,user,200)
        except:
            return JSONResponse("Internal Server Error",500)

    def put(self,username,deckname,card_id):
        try:
            new_question=request.form.get("new_question")
            new_answer=request.form.get("new_answer")

            errors=validateCardData(new_question,new_answer)
            if errors!={}:
                return JSONResponse(errors,400)

            user=Users.query.filter_by(username=username).first()
            if user==None:
                return JSONResponse("User not found",404)

            deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
            if deck==None:
                return JSONResponse("Deck not found",404)

            card=Cards.query.filter_by(card_id=card_id,deck_id=deck.deck_id).first()
            if card==None:
                return JSONResponse("Card not found",404)

            duplicate_card=Cards.query.filter_by(deck_id=deck.deck_id,question=new_question,answer=new_answer).first()
            if duplicate_card!=None:
                return JSONResponse("Card already exists for user",409)

            card.question=new_question
            card.answer=new_answer
            db.session.commit()

            return CardAPI.POST_CARD_TEMPLATE(card,deck,user,200)
        except:
            return JSONResponse("Internal Server Error",500)

    def delete(self,username,deckname,card_id):
        try:
            user=Users.query.filter_by(username=username).first()
            if user==None:
                return JSONResponse("User not found",404)

            deck=Decks.query.filter_by(deckname=deckname,user_id=user.user_id).first()
            if deck==None:
                return JSONResponse("Deck not found",404)

            card=Cards.query.filter_by(card_id=card_id,deck_id=deck.deck_id).first()
            if card==None:
                return JSONResponse("Card not found",404)

            db.session.delete(card)
            db.session.commit()

            return JSONResponse("Successfully Deleted",200)
        except:
            return JSONResponse("Internal Server Error",500)







class UserAPI(Resource):
    def USER_TEMPLATE(user,error_code):
        value={
            "user_id":user.user_id,
            "username":user.username
        }
        return JSONResponse(value,error_code)

    def post(self):
        username=request.form.get("username")
        password=request.form.get("password")

        errors=validateUserData(username,password)
        if errors!={}:
            return JSONResponse(errors,400)

        try:
            duplicate_user=Users.query.filter_by(username=username).first()
            if duplicate_user!=None:
                return JSONResponse("Username already taken",409)
            new_user=Users(username=username,password=password)
            db.session.add(new_user)
            db.session.commit()
            user=Users.query.filter_by(username=username).first()
            return UserAPI.USER_TEMPLATE(user,201)
        except:
            return JSONResponse("Internal Server Error",500)

    def get(self,username):
        try:
            user=Users.query.filter_by(username=username).first()
            if user==None:
                return JSONResponse("User not found",404)
            return UserAPI.USER_TEMPLATE(user,200)
        except:
            return JSONResponse("Internal Server Error",500)

    def delete(self,username):
        try:
            password=request.form.get("password")
            user=Users.query.filter_by(username=username).first()
            if user==None:
                return JSONResponse("User not found",404)
            if user.password!=password:
                return JSONResponse("Incorrect password",400)

            user_decks=Decks.query.filter_by(user_id=user.user_id).all()
            for deck in user_decks:
                deck_cards=Cards.query.filter_by(deck_id=deck.deck_id).all()
                for card in deck_cards:
                    db.session.delete(card)
                db.session.delete(deck)
            db.session.delete(user)
            db.session.commit()
            return JSONResponse("User Deleted",200)
        except:
            return JSONResponse("Internal Server Error",500)