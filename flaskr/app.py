from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for, session, abort
from TwitterUserManager import TwitterUserManager
from decimal import Decimal
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
from pip._vendor import cachecontrol
import requests
from flask_paginate import Pagination, get_page_args
from DepressionDetector import DepressionDetector
from Chatbot import Chatbot
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
import pathlib

import mysql.connector

db_config = {
    'user': 'uxo2ihlb0xdfqqsl',
    'password': 'hxrJaC3zfpXk8yVJ9iAv',
    'host': 'b6l5dugohgvzb9gw6u4o-mysql.services.clever-cloud.com',
    'database': 'b6l5dugohgvzb9gw6u4o',
}


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://alxcript_da_use:da*use10@mysql-alxcript.alwaysdata.net/alxcript_depresion_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Authentication

app.secret_key = "depressionapp"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = "871624759111-t7pa90fse2ahr5dg2rrc5hh576rc91rh.apps.googleusercontent.com"

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file = client_secrets_file, 
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://5000-alxcript-depressionapp-1yj4bhu0xju.ws-us98.gitpod.io/callback"
    )


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401) # Authorization required
        else:
            return function()
    
    return wrapper


@app.route("/authenticate-google")
def authenticateGoogle():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/login-comun", methods=['POST'])
def login_comun():
    dni = request.form["dni"]
    password = request.form["password"]

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM USUARIO WHERE dni = %s and contrasena = %s", (dni, password))
    usuariosCoincidentes = cursor.fetchall()

    cursor.close()
    connection.close()

    if(usuariosCoincidentes.count == 0):
        return "no hay usuarios encontrados"

    if(usuariosCoincidentes[0][7] == "Administrador"):
        return redirect("/admin")
    else:
        session["name"] = usuariosCoincidentes[0][1]
        session["email"] = "email_usuario@gmail.com"
        session["picture"] = usuariosCoincidentes[0][4]
        return render_template("usuario/index.html")


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500) # State does not match
    
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_token(
        id_token = credentials.id_token,
        request = token_request,
        audience=GOOGLE_CLIENT_ID
        )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["picture"] = id_info.get("picture")

    if(userNotExist(id_info.get("sub"))):
        registrarUsuarioNuevo(id_info.get("name"), 'usuario_google', id_info.get("at_hash"), id_info.get("picture"), id_info.get("sub"))

    usuarioId_DiagnosticoId = getUsuarioIdAndDiagnosticoIdByGoogleId(id_info.get("sub"))
    session["usuario_actual_id"] = usuarioId_DiagnosticoId[0]['usuarioId']
    session["id_diagnostico"] = usuarioId_DiagnosticoId[0]['diagnosticoId']

    return redirect("/usuario")

def userNotExist(google_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM USUARIO WHERE id_google = %s", (google_id,))
    usuariosCoincidentes = cursor.fetchall()

    cursor.close()
    connection.close()

    return len(usuariosCoincidentes) == 0

def registrarUsuarioNuevo(nombre, dni, contrasena, imagen, id_google):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    add_usuario = ("INSERT INTO USUARIO "
               "(nombre, dni, contrasena, imagen, id_google, estado, tipo) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")

    data_usuario = (nombre, dni, contrasena, imagen, id_google, 'Activo', 'Paciente')
    cursor.execute(add_usuario, data_usuario)
    usuarioRegistradoId = cursor.lastrowid


    add_diagnostico = ("INSERT INTO DIAGNOSTICO "
                "(id_usuario) "
                "VALUES (%s)")
    data_diagnostico = (usuarioRegistradoId,)

    cursor.execute(add_diagnostico, data_diagnostico)

    connection.commit()
    cursor.close()
    connection.close()

def getUsuarioIdAndDiagnosticoIdByGoogleId(id_google):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = ("SELECT USUARIO.id, DIAGNOSTICO.id FROM USUARIO INNER JOIN DIAGNOSTICO ON USUARIO.id = DIAGNOSTICO.id_usuario WHERE id_google = %s")
    cursor.execute(query, (id_google,))

    values = []
    for row in cursor:
        values.append({'usuarioId': row[0], 'diagnosticoId': row[1]})

    cursor.close()
    connection.close()

    return values

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/registro")
def registro():
    return render_template('registro.html')

@app.route("/protected_area")
@login_is_required
def protected_area():
    return "Protected page! hi " + session["name"] + " <a href='/logout'><button>Logout</button></a><p><img src='" + session["picture"] + "  ' /></p>"

#Administracion

@app.route("/")
def home():
    return render_template("login.html")


@app.route('/admin')
def admin_home():
    # Establecer la conexión a la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()


    # Ejecutar la consulta SQL
    query = "SELECT U.nombre, U.dni, DD.id_etapa, DD.score_etapa, DD.estado_etapa, U.imagen FROM USUARIO U JOIN DIAGNOSTICO D ON U.id = D.id_usuario JOIN DETALLES_DIAGNOSTICO DD ON D.id = DD.id_diagnostico"
    
    cursor.execute(query)
    detalles_list = cursor.fetchall()

    # Imprimir los detalles obtenidos
    for detalle in detalles_list:
        print(detalle)

    # Cerrar el cursor y la conexión a la base de datos
    cursor.close()
    connection.close()

    return render_template('admin/index.html', detalles_list=detalles_list)



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

    id_usuario=int(session["usuario_actual_id"])
    
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query_etapas_asignadas = "SELECT id_etapa FROM DETALLES_DIAGNOSTICO WHERE id_diagnostico IN (SELECT id FROM DIAGNOSTICO WHERE id_usuario = %s)"
    cursor.execute(query_etapas_asignadas, (id_usuario,))
    etapas_asignadas = [row[0] for row in cursor.fetchall()]

    # Consultar todas las etapas en la tabla ETAPA
    query_etapas = "SELECT id, tema FROM ETAPA"
    cursor.execute(query_etapas)
    etapa_list = cursor.fetchall()
    completadas_count = len(etapas_asignadas)
    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()

    return render_template('usuario/etapa.html', etapa_list=etapa_list, etapas_asignadas=etapas_asignadas, completadas_count=completadas_count)

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
    numero = int(request.form.get('numero'))
    respuestas = []
    for i in range(1, 6):  # Reemplaza 5 por el número de preguntas que tengas
        respuesta = request.form.get(f'pregunta{i}')
        respuestas.append(int(respuesta))

    # Calcular el puntaje total
    score = sum(respuestas)

    # Guardar el puntaje en la base de datos
    id=int(session["id_diagnostico"])
    id_usuario = session["usuario_actual_id"]
    score = sum(respuestas)

    if score <= 7:
        clasificacion = "Muy bajo"
    elif score <= 11:
        clasificacion = "Bajo"
    elif score <= 15:
        clasificacion = "Moderado"
    elif score <= 19:
        clasificacion = "Alto"
    else:
        clasificacion = "Muy alto"

    
    # Guardar los detalles del diagnóstico en la base de datos
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "INSERT INTO DETALLES_DIAGNOSTICO (id_diagnostico, id_etapa, score_etapa, estado_etapa) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (id, numero, score, clasificacion))
    connection.commit()

    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()


    if numero==10:
        

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Consulta para calcular el score_final
        query = """
            SELECT SUM(dd.score_etapa * e.ponderacion) AS score_final
            FROM DETALLES_DIAGNOSTICO dd
            INNER JOIN ETAPA e ON dd.id_etapa = e.id
            WHERE dd.id_diagnostico = %s
        """

        cursor.execute(query, (id,))
        score_final = cursor.fetchone()[0]

        if score_final >= 17:
            clasificacion_final = "Muy alto riesgo de depresión"
        elif score_final >= 13:
            clasificacion_final = "Alto riesgo de depresión"
        elif score_final >= 9:
            clasificacion_final = "Moderado riesgo de depresión"
        elif score_final >= 5:
            clasificacion_final = "Bajo riesgo de depresión"
        else:
            clasificacion_final = "Muy bajo riesgo de depresión"

        # Actualizar el score_final en la tabla DIAGNOSTICO
        update_query = "UPDATE DIAGNOSTICO SET score_final = %s, estado_final = %s WHERE id = %s AND id_usuario = %s"
        cursor.execute(update_query, (score_final, clasificacion_final, id, id_usuario))
        connection.commit()

        # Cerrar la conexión a la base de datos
        cursor.close()
        connection.close()




    # Redirigir a la página de resultados
    return redirect(url_for('etapa'))


@app.route('/resultados/score=<float:score>&numero=<int:numero>')
def resultados(score, numero):
    return render_template('usuario/resultados.html', score=score, numero=numero)


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

    