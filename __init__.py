from flask import Flask,request,render_template,redirect,url_for,make_response,jsonify,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_restful import Resource, Api, marshal_with,fields
from flask_security import Security, SQLAlchemyUserDatastore, auth_required, hash_password
from flask_security.models import fsqla_v2 as fsqla
from os import path

db=SQLAlchemy()
user_datastore = "SQLAlchemyUserDatastore()"

def create_app():
	app=Flask(__name__)
	app.config['SECRET_KEY'] = "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
	app.config['SECURITY_PASSWORD_SALT'] = "146585145368132386173505678016728509634"
	app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///final_project.sqlite3"
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
	app.config["DEBUG"]=True

	db.init_app(app)
	api=Api(app)

	fsqla.FsModels.set_db_info(db)

	class Role(db.Model, fsqla.FsRoleMixin):
		pass

	class User(db.Model, fsqla.FsUserMixin):
		pass

	global user_datastore
	user_datastore = SQLAlchemyUserDatastore(db, User, Role)
	security = Security(app, user_datastore)

	from api import UserAPI, DeckAPI, CardAPI
	api.add_resource(DeckAPI,"/api/deck/create","/api/<string:username>/deck/<string:deckname>")
	api.add_resource(CardAPI,"/api/card/create","/api/<string:username>/deck/<string:deckname>/card/<int:card_id>")
	api.add_resource(UserAPI,"/api/user/create","/api/<string:username>")

	from views import views
	app.register_blueprint(views, url_prefix="/")

	if not path.exists("/final_project.sqlite3"):
		db.create_all(app=app)
	
	return  app, api

