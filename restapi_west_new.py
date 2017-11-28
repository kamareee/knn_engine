
import requests
from flask import Flask, render_template, make_response
# from flask.ext.pymongo import PyMongo
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

class BarAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('serviceID', type=str)
        json = parser.parse_args()
        serviceID = json.get('serviceID')#__getitem__('serviceID')
        # payload = {'serviceID': serviceID}
        r = requests.get('http://localhost:5001/getParam',params=json)
        # print(r.url)
        # val = urllib.unquote(r.url).decode('utf8')
        # print(val)
        # print(r.text)
        predictedClass = r.json().get('PredictedClass')
        advisory_action = r.json().get('Action')
        advisory_summary = r.json().get('Summary')
        advisory_prompt = r.json().get('Prompt')
        advisory_inbound = r.json().get('Inbound')
        advisory_escalation = r.json().get('NextEscalation')
        expertmatrix = r.json().get('ExpertMatrix')
        matchedmatrix = r.json().get('MatchMatrix')
        headers = {'Content-Type': 'text/xml'}
        # return parser.parse_args()
        return make_response(render_template('testxml.xml', summary=advisory_summary, predictedclass=predictedClass, action=advisory_action,
                                             prompt=advisory_prompt, inbound=advisory_inbound, nextescalation=advisory_escalation,
                                             expertmtx=expertmatrix, matchmtx=matchedmatrix), 200, headers)
        # return 'you are done 123'

api.add_resource(BarAPI, '/expert.do', endpoint='expert.do')
api.add_resource(BarAPI, '/getParam', endpoint='getParam')

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    # app.run('127.0.0.1', 5000, True)
    # app.run(debug=True)
    app.run('0.0.0.0', 5000, False)
