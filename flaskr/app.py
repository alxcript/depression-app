from flask import Flask, render_template, request, jsonify, make_response
import tweepy

app = Flask(__name__)

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

def searchUserInTwitter(username):
    print("Userna:[" + username + "]")
    consumer_key="FjXVroKiU4AerXAHae02OcUoz"
    consumer_secret="ofSa8wOHkzLIKi8s82gVjHEo1rLDKgNBTUO1OYI0gG9fhFnkQS"
    bearer_token="AAAAAAAAAAAAAAAAAAAAABrumQEAAAAA4ZoFwe1YCtfJj8EQj48Yy52%2FDFU%3DBA2Lg3n4UcIFkqSZfb16esmgKpzi0yAJYxzJU6TltrTz0b9S1l"
    access_token="4855557995-GdSPjgmNyn2im7KvAH6ZI7l2BE9TIMmKJDKanX7"
    access_token_secret="NB9brsICr4lKHJBB6404oJq3TCT9H7DmDiCqLskDoXW3A"

    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )

    api = tweepy.API(auth)

    listUsersFound = api.search_users(q=username)
    namesFound = []
    for user in listUsersFound:
        namesFound.append({"screen_name": user.screen_name, "profile_image_url": user.profile_image_url_https, "name": user.name})
    return namesFound

if __name__ == "__main__":
    app.run()