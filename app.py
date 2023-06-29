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
from flask import Flask, render_template, request
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split



import mysql.connector

db_config = {
    'user': '318180_admin',
    'password': '2019063317',
    'host': 'mysql-dbmental123.alwaysdata.net',
    'database': 'dbmental123_koala',
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
<<<<<<< HEAD
    redirect_uri="https://5000-alxcript-depressionapp-1yj4bhu0xju.ws-us101.gitpod.io/callback"
=======
    redirect_uri="https://5000-alxcript-depressionapp-xjakubcxflr.ws-us101.gitpod.io/callback"
>>>>>>> origin/main
    )


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401) # Authorization required
        else:
            return function()
    # Renaming the function name:
    wrapper.__name__ = function.__name__
    return wrapper


@app.errorhandler(401)
def custom_401(error):
    return render_template("exceptions/401.html")


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
    session["chat_activado"] = isChatActivado(session["id_diagnostico"])

    return redirect("/usuario")

def isChatActivado(id_diagnostico):

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM DETALLES_DIAGNOSTICO WHERE id_diagnostico = %s", (id_diagnostico,))
    modoDelaUltimaEtapa = "noregistrado"
    listaEtapasDelUsuario = cursor.fetchall()
    if(len(listaEtapasDelUsuario) > 0):
        modoDelaUltimaEtapa = listaEtapasDelUsuario.pop()[3].lower()
    print("modoDelaUltimaEtapa:", modoDelaUltimaEtapa)
    cursor.close()
    connection.close()

    isChatActivado = "no"
    if(modoDelaUltimaEtapa in ['moderado', 'alto', 'muy alto']):
        isChatActivado = "yes"
    
    return isChatActivado

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


@app.route('/admin/resultado/<int:usuario_id>')
def resultado(usuario_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Obtener los datos del paciente, el score final y la clasificación final de diagnóstico
    query_datos_paciente = """
        SELECT U.nombre, D.score_final, D.estado_final
        FROM USUARIO U
        JOIN DIAGNOSTICO D ON U.id = D.id_usuario
        WHERE U.id = %s
    """
    cursor.execute(query_datos_paciente, (usuario_id,))
    datos_paciente = cursor.fetchone()

    # Obtener los datos del diagnóstico y los detalles del diagnóstico
    query_diagnostico = """
        SELECT DD.id_etapa, E.tema, DD.score_etapa, DD.estado_etapa
        FROM DIAGNOSTICO D
        JOIN DETALLES_DIAGNOSTICO DD ON D.id = DD.id_diagnostico
        JOIN ETAPA E ON DD.id_etapa = E.id
        WHERE D.id_usuario = %s
        ORDER BY DD.id_etapa
    """
    cursor.execute(query_diagnostico, (usuario_id,))
    resultados = cursor.fetchall()

    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()

    return render_template('admin/resultado.html', datos_paciente=datos_paciente, resultados=resultados)
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
    query = "SELECT u.*, d.score_final, d.estado_final FROM USUARIO u JOIN DIAGNOSTICO d ON u.id = d.id_usuario WHERE u.tipo = 'Paciente'"
    cursor.execute(query)
    usuario_list = cursor.fetchall()

    # Cerrar el cursor y la conexión a la base de datos
    cursor.close()
    connection.close()
    return render_template('admin/tables.html', usuario_list=usuario_list)


@app.route("/usuario")
@login_is_required
def usuario():
    return render_template('usuario/etapa.html')

@app.route('/chat')
def chat():
    return render_template('usuario/chat.html')

@app.route('/etapa')
def etapa():

    id_usuario=int(session["usuario_actual_id"])

    prediction = request.args.get('prediction')
    porcentaje_cercania = request.args.get('porcentaje_cercania')
    score_final = request.args.get('score_final')
    
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query_etapas_asignadas = "SELECT COALESCE((SELECT MAX(id_etapa) + 1 FROM DETALLES_DIAGNOSTICO WHERE id_diagnostico IN (SELECT id FROM DIAGNOSTICO WHERE id_usuario = %s)), 1) AS next_id_etapa;"
    
    cursor.execute(query_etapas_asignadas, (id_usuario,))
    etapas_asignadas = [row[0] for row in cursor.fetchall()]

    # Consultar todas las etapas en la tabla ETAPA
    query_etapas = "SELECT id, tema, imagen FROM ETAPA"
    cursor.execute(query_etapas)
    etapa_list = cursor.fetchall()
    completadas_count = int(etapas_asignadas[0])
    # Cerrar la conexión a la base de datos
    cursor.close()
    connection.close()

    return render_template('usuario/etapa.html', etapa_list=etapa_list, etapas_asignadas=etapas_asignadas, completadas_count=completadas_count,prediction=prediction, porcentaje_cercania=porcentaje_cercania, score_final=score_final)

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
        csv_path = os.path.join(app.root_path, 'static', 'datos.csv')
        # Cargar los datos del archivo CSV
        df = pd.read_csv(csv_path, encoding='ISO-8859-1')

        # Dividir los datos en características (X) y etiquetas (y)
        X = df.drop('Score Final', axis=1)
        y = df['Score Final']

        # Dividir los datos en conjuntos de entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Crear un objeto de regresión lineal
        model = LinearRegression()

        # Entrenar el modelo con los datos de entrenamiento
        model.fit(X_train, y_train)

        # Conectar a la base de datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Ejecutar la consulta SQL para obtener los datos del usuario
        query = """
        SELECT
        U.id AS id_usuario,
        D.score_final,
        DD.score_etapa AS etapa_1,
        DD2.score_etapa AS etapa_2,
        DD3.score_etapa AS etapa_3,
        DD4.score_etapa AS etapa_4,
        DD5.score_etapa AS etapa_5,
        DD6.score_etapa AS etapa_6,
        DD7.score_etapa AS etapa_7,
        DD8.score_etapa AS etapa_8,
        DD9.score_etapa AS etapa_9,
        DD10.score_etapa AS etapa_10
        FROM
        USUARIO U
        JOIN DIAGNOSTICO D ON U.id = D.id_usuario
        LEFT JOIN DETALLES_DIAGNOSTICO DD ON D.id = DD.id_diagnostico AND DD.id_etapa = 1
        LEFT JOIN DETALLES_DIAGNOSTICO DD2 ON D.id = DD2.id_diagnostico AND DD2.id_etapa = 2
        LEFT JOIN DETALLES_DIAGNOSTICO DD3 ON D.id = DD3.id_diagnostico AND DD3.id_etapa = 3
        LEFT JOIN DETALLES_DIAGNOSTICO DD4 ON D.id = DD4.id_diagnostico AND DD4.id_etapa = 4
        LEFT JOIN DETALLES_DIAGNOSTICO DD5 ON D.id = DD5.id_diagnostico AND DD5.id_etapa = 5
        LEFT JOIN DETALLES_DIAGNOSTICO DD6 ON D.id = DD6.id_diagnostico AND DD6.id_etapa = 6
        LEFT JOIN DETALLES_DIAGNOSTICO DD7 ON D.id = DD7.id_diagnostico AND DD7.id_etapa = 7
        LEFT JOIN DETALLES_DIAGNOSTICO DD8 ON D.id = DD8.id_diagnostico AND DD8.id_etapa = 8
        LEFT JOIN DETALLES_DIAGNOSTICO DD9 ON D.id = DD9.id_diagnostico AND DD9.id_etapa = 9
        LEFT JOIN DETALLES_DIAGNOSTICO DD10 ON D.id = DD10.id_diagnostico AND DD10.id_etapa = 10
        WHERE
        U.id = %s
        """
        cursor.execute(query, (id_usuario,))
        data = cursor.fetchone()

        # Cerrar la conexión a la base de datos
        cursor.close()
        conn.close()

        # Datos de prueba
        X_test = pd.DataFrame({
            'Autoevaluación': [data[2]],
            'Relaciones interpersonales': [data[3]],
            'Actividades diarias': [data[4]],
            'Autoestima': [data[5]],
            'Estrés y afrontamiento': [data[6]],
            'Sueño y descanso': [data[7]],
            'Salud física': [data[8]],
            'Metas y aspiraciones': [data[9]],
            'Resiliencia': [data[10]],
            'Satisfacción con la vida': [data[11]]
        })

        # Realizar predicciones en el conjunto de prueba
        predictions = model.predict(X_test)

        # Valor para comparar
        valor_real = score_final

        # Calcular el porcentaje de cercanía a la realidad
        porcentaje_cercania = (1 - abs(float(predictions) - float(valor_real)) / float(valor_real)) * 100

        # Redondear la predicción y el porcentaje de cercanía a 2 decimales
        prediction = round(predictions[0], 2)
        porcentaje_cercania = round(porcentaje_cercania, 2)
        return redirect(url_for('etapa', prediction=prediction, porcentaje_cercania=porcentaje_cercania,score_final=score_final))




    session["chat_activado"] = isChatActivado(session["id_diagnostico"])

    if(clasificacion not in ["Moderado", "Alto", "Muy alto"]):
        # Redirigir a la página de resultados
        return redirect(url_for('etapa'))

    return render_template('usuario/chat.html', clasificacion=clasificacion)
    


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
    modo = "Muy alto"
    response = chatbot.generateResponse(request.json["query"], modo)
    return jsonify({
        "response": response,
        "datetime": datetime.datetime.now()
    })

if __name__ == "__main__":
    app.run()

    