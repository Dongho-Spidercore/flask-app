from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
from elasticsearch import Elasticsearch
import json
import QueryBundle as qb

app = Flask(__name__)
#CORS(app)

#es = Elasticsearch(hosts='http://elastic:tlfldntm@115.91.133.190:9200/')
es = Elasticsearch(hosts='https://spidercore:tlfldntm@192.168.0.201:9200/')
indexDisease = 'disease_test'
indexDrug = 'drug_test'

@app.route('/', methods=['OPTIONS', 'GET'])
#@cross_origin()
def launch():
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'GET':
        param_dict = request.args.to_dict()
        print(param_dict['source'])
        param_dict = json.loads(param_dict['source'])
        #req = request.get_json()
        inputType = param_dict['type']
        inputName = param_dict['name']
        
        if inputType == 'drug':
            res = qb.searchDrugInfo(inputName)
            #print(res)
        elif inputType == 'disease':
            res = qb.searchDiseaseInfo(inputName)
            #print(res)
        elif inputType == 'chemical':
            res = qb.searchChemicalInfo(inputName)
        elif inputType == 'protein':
            res = qb.searchProteinInfo(inputName)
        elif inputType == 'gene':
            res = qb.searchGeneInfo(inputName)
        elif inputType == 'mRNA':
            res = qb.searchmRNAInfo(inputName)


        return build_actual_response(res)

"""
@app.route('/<username>')
def test1(username):
    return 'test %s' % username

@app.route('/search', methods=['GET'])
def search():
    name = request.args.get('name')
    treatFlag = request.args.get('treat')
    identifier = qb.checkDiseaseOrDrug(name)

    if identifier == 0:
        qb.searchDiseasesByDrug(name, treatFlag)
    elif identifier == 1:
        qb.searchDrugsByDisease(name, treatFlag)
    else:
        return 'Input Not Found'

@app.route('/search/disease/<diseasename>', methods=['GET'])
def searchDisease(diseasename):
    json_string = query(es, indexDisease, diseasename)
    json_object = jsonify(json_string['hits']['hits'])

    return json_object

@app.route('/search/drug/<drugname>', methods=['GET'])
def searchDrug(drugname):
    json_string = query(es, indexDrug, drugname)
"""
def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def build_actual_response(res):
    response = make_response(jsonify(res), 200)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def query(es, index, spider) -> dict:
    body = {
        "query": {
            "match": {
                "spider id": spider
            }
        }
    }
    res = es.search(index=index, body=body)
    print(res)
    return res

if __name__ == '__main__':
    #app.run(debug=True, host='192.168.0.4', port=5388)
    app.run(debug=True, host='0.0.0.0')
