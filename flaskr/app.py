from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from TwitterUserManager import TwitterUserManager
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate

# create the extension
db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://alxcript_da_use:da*use10@mysql-alxcript.alwaysdata.net/alxcript_depresion_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize the app with the extension
db.init_app(app)

from models import User, DepresionScore, TwitterUser, Tweet, PatientData

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/admin')
def admin_home():
    return render_template('admin/index.html')
@app.route('/admin/RegistroPacientes')
def admin_RegistroPacientes():
    return render_template('admin/forms.html')
@app.route('/admin/GestionarPacientes')
def admin_GestionarPacientes():
    return render_template('admin/tables.html')




@app.get("/formulario")
def formulario():
    return render_template("formulario.html")

@app.route("/search-twitter-accounts", methods=["POST"])
def getUsersByUsername():
    req = request.get_json()
    print(req)
    usuariosEncontrados = searchUserInTwitter(req["username"])
    res = make_response(jsonify({"data": usuariosEncontrados}), 200)
    print(usuariosEncontrados)
    return res

@app.route("/users/create", methods=["GET", "POST"])
def users_create():
    print("creating user..")
    if request.method == "POST":
        user = User(
            nickname="MyNick",
            email=request.form["email"],
            password="1234",
            patients=[PatientData(
                fullname = request.form["firstname"],
                gender = request.form["gender"]
            )]
        )
        print("storing user in db")
        print(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("formulario.html")

def searchUserInTwitter(username):
    consumer_key="FjXVroKiU4AerXAHae02OcUoz"
    consumer_secret="ofSa8wOHkzLIKi8s82gVjHEo1rLDKgNBTUO1OYI0gG9fhFnkQS"
    access_token="4855557995-GdSPjgmNyn2im7KvAH6ZI7l2BE9TIMmKJDKanX7"
    access_token_secret="NB9brsICr4lKHJBB6404oJq3TCT9H7DmDiCqLskDoXW3A"
    twitter_manager = TwitterUserManager(api_key=consumer_key, api_secret_key=consumer_secret, access_token=access_token, access_token_secret=access_token_secret)
    #print(twitter_manager.get_tweets(1499586805))
    return twitter_manager.search_users(username)

if __name__ == "__main__":
    app.run()