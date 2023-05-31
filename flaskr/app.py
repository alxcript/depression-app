from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
from TwitterUserManager import TwitterUserManager

from DepressionDetector import DepressionDetector
from Chatbot import Chatbot
from flask_sqlalchemy import SQLAlchemy
import datetime


import mysql.connector

db_config = {
    'user': 'uxo2ihlb0xdfqqsl',
    'password': 'hxrJaC3zfpXk8yVJ9iAv',
    'host': 'b6l5dugohgvzb9gw6u4o-mysql.services.clever-cloud.com',
    'database': 'b6l5dugohgvzb9gw6u4o',
}


#from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate


# create the extension
#db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://alxcript_da_use:da*use10@mysql-alxcript.alwaysdata.net/alxcript_depresion_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize the app with the extension
#db.init_app(app)

#from models import User, DepresionScore, TwitterUser, Tweet, PatientData

#with app.app_context():
 #   db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/admin')
def admin_home():
    return render_template('admin/index.html')
@app.route('/admin/RegistroPacientes')
def admin_RegistroPacientes():
    return render_template('admin/forms.html')

@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():

 # Obtén los datos enviados desde el formulario
    nombre = request.form['nombres']
    apellido = request.form['apellidos']
    dni = request.form['dni']
    contrasena = request.form['contrasena']
    imagen = request.form['imagen']
    tipo="Paciente"
    estado="Activo"
    nombres=nombre+apellido

    # Realiza la inserción en la base de datos
    try:
        # Establece la conexión a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Inserta los datos en la tabla USUARIO
        query = "INSERT INTO USUARIO (nombre, dni, contrasena, imagen,tipo,estado) VALUES (%s,%s, %s, %s, %s, %s)"
        values = (nombres, dni, contrasena, imagen,tipo,estado)
        cursor.execute(query, values)
        
        # Guarda los cambios en la base de datos
        connection.commit()

        # Cierra el cursor y la conexión a la base de datos
        cursor.close()
        connection.close()

        # Devuelve una respuesta JSON para indicar el éxito del registro
        response = {'success': True, 'message': 'Registro exitoso'}
        return jsonify(response)

    except Exception as e:
        # En caso de error, devuelve una respuesta JSON con el mensaje de error
        response = {'success': False, 'message': str(e)}
        return jsonify(response)


@app.route('/admin/GestionarPacientes')
def admin_GestionarPacientes():
    # Establecer la conexión a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Ejecutar la consulta SQL
    query = "SELECT * FROM USUARIO WHERE tipo='Paciente'"
    cursor.execute(query)
    usuario_list = cursor.fetchall()

    # Cerrar el cursor y la conexión a la base de datos
    cursor.close()
    connection.close()
    return render_template('admin/tables.html', usuario_list=usuario_list)


@app.route('/usuario')
def usuario():
    return render_template('usuario/etapa.html')

@app.route('/chat')
def chat():
    return render_template('usuario/chat.html')

@app.route('/etapa')
def etapa():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT * FROM ETAPA"
    cursor.execute(query)
    etapa_list = cursor.fetchall()

    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()

    # Pasar los datos a la plantilla etapa.html
    return render_template('usuario/etapa.html', etapa_list=etapa_list)

@app.route('/quiz')
def quiz():
    return render_template('quiz/index.php')

@app.route('/etapa/<int:numero>')
def etapaQz(numero):
    # Realizar la consulta a la base de datos para obtener las preguntas de la etapa
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT P.pregunta_descripcion, E.tema, P.id FROM PREGUNTA AS P INNER JOIN ETAPA AS E ON P.id_etapa = E.id WHERE E.id = %s"
    cursor.execute(query, (numero,))
    results = cursor.fetchall()

    # Obtener los IDs de las preguntas de la etapa 1
    preguntas_etapa_1_ids = [row[2] for row in results]

    # Obtener la estructura de calificación correspondiente a los IDs de las preguntas de la etapa 1
    estructura_calificacion = []
    for pregunta_id in preguntas_etapa_1_ids:
        cursor.execute("SELECT nombre, puntaje FROM ESTRUCTURA_CALIFICACION WHERE id_pregunta = %s", (pregunta_id,))
        calificaciones = cursor.fetchall()
        estructura_calificacion.extend(calificaciones)

    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()

    return render_template('usuario/cuestionario.html', results=results, estructura_calificacion=estructura_calificacion, numero=numero)



@app.route('/submit', methods=['POST'])
def submit():
    # Obtener los valores de las respuestas del formulario
    numero = request.form.get('numero')
    respuestas = []
    for i in range(1, 6):  # Reemplaza 5 por el número de preguntas que tengas
        respuesta = request.form.get(f'pregunta{i}')
        respuestas.append(int(respuesta))

    # Calcular el puntaje total
    puntaje_total = sum(respuestas)

    # Guardar el puntaje en la base de datos
    #id=session['usuario_actual_id']




    # Calcular el score en base al valor de 'numero'
    if numero == 1:
        score = puntaje_total * 0.2
    elif numero == 2:
        score = puntaje_total * 0.1
    elif numero == 3:
        score = puntaje_total * 0.15
    elif numero == 4:
        score = puntaje_total * 0.3
    elif numero == 5:
        score = puntaje_total * 0.25
    elif numero == 6:
        score = puntaje_total * 0.1
    elif numero == 7:
        score = puntaje_total * 0.15
    elif numero == 8:
        score = puntaje_total * 0.2
    elif numero == 9:
        score = puntaje_total * 0.25
    elif numero == 10:
        score = puntaje_total * 0.15
    else:
        # Manejar caso de número inválido
        score = 0
    # Guardar los detalles del diagnóstico en la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "INSERT INTO DETALLES_DIAGNOSTICO (id_diagnostico, id_etapa, score_etapa, estado_etapa) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (id_diagnostico, numero, score, clasificacion))
    connection.commit()

    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()


    # Redirigir a la página de resultados
    return redirect(f'/resultados/{numero}?score={score}')

# Ruta para mostrar los resultados
@app.route('/resultados')
def resultados():
    # Obtener el puntaje desde la base de datos
    score = int(request.args.get('score'))

    return render_template('usuario/resultados.html', score=score)








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
    response = chatbot.generateResponse(request.json["query"])
    return jsonify({
        "response": response,
        "datetime": datetime.datetime.now()
    })

if __name__ == "__main__":
    app.run()

    