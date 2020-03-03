import pickle
import re,os
import numpy as np
from flask import Flask, request, jsonify, make_response
from flask_jwt import jwt
import datetime
from   waitress import serve
from functools import wraps
import psycopg2
from passlib.context import CryptContext
# from flask_cors import CORS
from sklearn.feature_extraction.text import CountVectorizer


def db_writer(q,data):
    connection = psycopg2.connect(user="postgres",
                                  password="postgres",
                                  host="localhost",
                                  port="5433",
                                  database='mfdm')
    cursor = connection.cursor()
    cursor.execute(q,data)
    connection.commit()
    count = cursor.fetchone()
    # print("you are connected to -",count,"\n")
    return count

encrypted_password = db_writer("select username,password from cred_vault where sno = %s",('3',))
pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)


def comma_tokenizer(token_list):
    return token_list.split(",")


group_model = pickle.load(open(os.path.join('models', 'modeloldfile13.01.2020.pk'), 'rb'))
group_vector = pickle.load(open(os.path.join('models', 'vectorizeroldfile13.01.2020.pk'), 'rb'))


def preprocess(string, *special_tokens):
    string = re.sub('[^a-zA-Z ]+', '', string)
    string = re.sub('\s+', ' ', string)
    tokens = string.split(" ")
    tokens = [word.lower() if not word.isupper() else word for word in tokens]
    for token in special_tokens:
        tokens.append(token)
    string = ','.join(tokens)
    return string


def token_required(f):
    @wraps(f)
    def validate():
        token = request.headers.get('authorization')
        if not token:
            return jsonify({'message':'Token is missing'}),403
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is missing or invalid'}),403
        return f()
    return validate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Eicesecretkey'


@app.route('/agl')
def hel():
    return 'Hello world!! This is EICE'


@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    valid_user = check_encrypted_password(auth.password,encrypted_password[1])
    if auth.username == encrypted_password[0] and valid_user is True:
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},app.config['SECRET_KEY'])
        return token.decode('UTF-8')
    return make_response('Unauthorized',401)


@app.route('/ags', methods=['POST'])
@token_required
def fin():
    summar = request.json['sum']
    return summar


@app.route('/ag', methods=['POST'])
@token_required
def find_cti():
    sum = request.json['Summary']
    group_summary = preprocess(sum)
    # print(type(group_summary))
    x = [group_summary]
    # print(x)
    # print(group_summary)
    group_x = group_vector.transform([group_summary])
    # print(group_x)
    group = group_model.predict(group_x)[0]
    # print(type(group))
    # return group_x
    prob_conf = np.max(group_model.predict_proba(group_x)) * 100
    try:

        data = (sum, group, prob_conf)
        y = db_writer("INSERT  INTO eice_webservice (summary,eice_predicted_output,probobility_score) values (%s,%s,"
                       "%s);", data)

        return jsonify({"group": group,"prob_conf":prob_conf})

    except:
        return jsonify({"group": group,"prob_conf":prob_conf})


if __name__ == '__main__':
    serve(app,host='0.0.0.0', port='5050')
