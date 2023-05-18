from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from TwitterUserManager import TwitterUserManager
from DepressionDetector import DepressionDetector
from Chatbot import Chatbot
from flask_sqlalchemy import SQLAlchemy
import datetime

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
        consumer_key="0UnkO55lofzPjPtX3zpmd4xRt"
        consumer_secret="ACloPt81xa4USf6PIutsIThrMODZrdA1ytHY55wGYlusDlfiIT"
        access_token="4855557995-NEvKeV12hruDOoLbrn36hAzQL1KWIStWnezLDJE"
        access_token_secret="LmdFUtUjqnI6u7t2aGBtAMa1PfIFK534HloxbPt7XwEu0"
        twitter_manager = TwitterUserManager(api_key=consumer_key, api_secret_key=consumer_secret, access_token=access_token, access_token_secret=access_token_secret)
        tweets = twitter_manager.get_tweets(request.form["twitter-screen-name"])
        
        depression_detector = DepressionDetector()
        #depression_detector.predict("bad")
        resultados_analizados = []
        for tweet in tweets:
            analized = depression_detector.predict(tweet["full_text"])
            resultados_analizados.append({'text': tweet["full_text"], 'res': analized})
        
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
        return render_template("resultados.html", len = len(resultados_analizados), TweetsList = resultados_analizados)

    return render_template("formulario.html")

@app.route("/resultados-twitter", methods=["GET"])
def resultados_twitter():
    return render_template("resultados.html")


def searchUserInTwitter(username):
    consumer_key="0UnkO55lofzPjPtX3zpmd4xRt"
    consumer_secret="ACloPt81xa4USf6PIutsIThrMODZrdA1ytHY55wGYlusDlfiIT"
    access_token="4855557995-NEvKeV12hruDOoLbrn36hAzQL1KWIStWnezLDJE"
    access_token_secret="LmdFUtUjqnI6u7t2aGBtAMa1PfIFK534HloxbPt7XwEu0"
    twitter_manager = TwitterUserManager(api_key=consumer_key, api_secret_key=consumer_secret, access_token=access_token, access_token_secret=access_token_secret)
    return twitter_manager.search_users(username)



@app.route("/generate-chatbot-response", methods=["POST"])
def generateResponseChatbot():
    chatbot = Chatbot()
    response = chatbot.generateResponse(request.form["query"])
    return make_response(
        jsonify(
            {
                "response": response,
                "datetime": datetime.datetime.now()
            }), 
            200
        )

if __name__ == "__main__":
    app.run()