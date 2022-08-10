from flask import jsonify
from elasticsearch import Elasticsearch
import json

#es = Elasticsearch(hosts='http://elastic:tlfldntm@115.91.133.190:9200/')
es = Elasticsearch(hosts='https://spidercore:tlfldntm@192.168.0.201:9200/')
indexDisease = 'disease_test_v2'
indexDrug = 'drug_test'
indexChemical = 'chemical_test'
indexProtein = 'protein_test'
indexGene = 'gene_test'
indexMRNA = 'mrna_test'

def checkDiseaseOrDrug(name):
    
    res = query(es, indexDrug, name)
    res_json = json.loads(json.dumps(res['hits']))
    
    #print(res_json)

    if res_json['total']['value'] != 0:
        return 0 # input is drug
    
    res = query(es, indexDisease, name)
    res_json = json.loads(json.dumps(res['hits']))

    if res_json['total']['value'] != 0:
        return 1 # input us disease
    
    return 2 # input not found

def query(es, index, name):
    body = {
        "query": {
            "match": {
                "name.name": name
            }
        }
    }

    res = es.search(index=index, body=body)
    #print(res)
    return res

def hasJsonKeyProperty(json, key):
    try:
        buf = json[key]
    except KeyError:
        print('json has not the key :' + key)
        return False
    print('json has the key :' + key)
    return True

def getDrugRelation(treatFlag, relation):
    if treatFlag == 0: # Treat
        if relation == 'indication': return 0
        elif relation == 'off-label use': return 1
    elif treatFlag == 1: # Sider Effect
        if relation == 'contraindication': return 0
    else: #General Info Control
        print('Relation Flag is not 0 or 1')
    return -1

def searchDrugInfo(name):
    res = query(es, indexDrug, name)
    res_json = json.loads(json.dumps(res['hits']))
    res_json = res_json['hits']
    return res_json

def searchDiseaseInfo(name):
    body = {
        "query": {
            "match": {
                "synonyms.exact.val": name
            }
        }
    }
    res = es.search(index=indexDisease, body=body)
    res_json = json.loads(json.dumps(res['hits']))
    res_json = res_json['hits']
    return res_json

def searchChemicalInfo(name):
    body = {
        "query": {
            "match": {
                "synonyms.val": name
            }
        }
    }
    res = es.search(index=indexChemical, body=body)
    res_json = json.loads(json.dumps(res['hits']))
    res_json = res_json['hits']
    return res_json

def searchProteinInfo(name):
    body = {
        "query": {
            "match": {
                "names_taxonomy.protein.name.val": name
            }
        }
    }
    res = es.search(index=indexProtein, body=body)
    res_json = json.loads(json.dumps(res['hits']))
    res_json = res_json['hits']
    return res_json

def searchGeneInfo(name):
    return ''

def searchmRNAInfo(name):
    body = {
        "query": {
            "match": {
                "Stem-loop.ID.val": name
            }
        }
    }
    res = es.search(index=indexMRNA, body=body)
    res_json = json.loads(json.dumps(res['hits']))
    res_json = res_json['hits']
    return res_json

def searchDrugsByDisease(name, treatFlag):
    res = query(es, indexDisease, name)
    res_json = json.loads(json.dumps(res['hits']))
    res_json = res_json['hits'][0]['_source']

    diseaseId = res_json['spider id']
    print(diseaseId)
    
    body = {
        "query": {
            "match": {
                "Drug Use.spider id": diseaseId
            }
        }
    }
    res = es.search(index=indexDrug, body=body)
    res_json = json.loads(json.dumps(res['hits']))

    if res_json['total']['value'] == 0:
        # No result of spider id
        print('No result')
    else:
        res_json_list = res_json['hits']
        drugListRelated = []
        for drug in res_json_list:
            drugUseList = drug['_source']['Drug Use']

            for drugUse in drugUseList:
                if not hasJsonKeyProperty(drugUse, 'spider id'):
                    print('No spider Id for Drug Use Element -- Disease:' + drugUse['Disease'])
                    continue
                if drugUse['spider id'] == diseaseId:
                    drugRelationFlag = getDrugRelation(treatFlag, drugUse['Relation'])
                    
                    if drugRelationFlag == 0: # Add element front
                        drugListRelated.insert(0, drug)
                    elif drugRelationFlag == 1: # Add element rear
                        drugListRelated.append(drug)
                    #print(drug)
                    break
        return drugListRelated

def searchDiseasesByDrug(name, treatFlag):
    res = query(es, indexDrug, name)
    res_json = json.loads(json.dumps(res['hits']))
    res_json = res_json['hits'][0]['_source']

    drugId = res_json['spider id']
    print(drugId)

    diseaseList = res_json['Drug Use']
    diseaseListRelated = []
    
    for disease in diseaseList:
        if not hasJsonKeyProperty(disease, 'spider id'):
            print('No spider Id for Drug Use Element -- Disease:' + disease['Disease'])
            continue
        diseaseRelationFlag = getDrugRelation(treatFlag, disease['Relation'])
        if diseaseRelationFlag == 0: # Add Element front
            diseaseListRelated.insert(0, disease)
        elif diseaseRelationFlag == 1: # Add Element rear
            diseaseListRelated.append(disease)
        break
    
    diseaseListFinal = []
    for disease in diseaseListRelated:
        body = {
            "query": {
                "match": {
                    "spider id": disease['spider id']
                }
            }
        }
        res = es.search(index=indexDisease, body=body)
        res_json = json.loads(json.dumps(res['hits']))
        res_json = res_json['hits'][0]
        print(res_json)
        diseaseListFinal.append(res_json)
    return diseaseListFinal





