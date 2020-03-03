import pickle
import os
import re
from flask import Flask, request, jsonify
import json
# from flask_cors import CORS
from sklearn.feature_extraction.text import CountVectorizer


def comma_tokenizer(token_list):
    return token_list.split(",")


group_model = pickle.load(open(os.path.join('models', 'model03.09.2019.pk'), 'rb'))
group_vector = pickle.load(open(os.path.join('models', 'vectorizer03.09.2019.pk'), 'rb'))


def preprocess(string, *special_tokens):
    # print(string, special_tokens)
    string = re.sub('[^a-zA-Z ]+', '', string)
    string = re.sub('\s+', ' ', string)
    print(string)
    tokens = string.split(" ")
    tokens = [word.lower() if not word.isupper() else word for word in tokens]
    print(tokens)
    for token in special_tokens:
        tokens.append(token)
    string = ','.join(tokens)
    print(string)
    return string


app = Flask(__name__)
# CORS(app)


@app.route('/agl')
def hel():
    return 'hello world'


@app.route('/ags', methods=['POST'])
def fin():
#print(json.loads('sum'))
    summar = request.json['sum']
    return summar


@app.route('/ag', methods=['POST'])
def find_cti():
    print(request.json)
    sum = request.json['summary']
    # summary = 'Deactivate Kellie Benda’s Yammer account'
    print(sum)
    # ppv=[service,request,implement,SAP,note,to,see,the,links,in,APD]
    # ppv1=['service,request,implement,SAP,note,to,see,the,links,in,APD']
    group_summary = preprocess(sum)
    print(type(group_summary))
    x = [group_summary]
    print(x)
    print(group_summary)
    group_x = group_vector.transform([group_summary])
    print(group_x)
    group = group_model.predict(group_x)[0]
    print(type(group))
    # return group_x
    return jsonify({"group": group})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5050', debug='true')
