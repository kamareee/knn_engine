import requests
from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

# @app.route('/getParam', methods=['GET'])
class BarAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('serviceID', type=str)
        json = parser.parse_args()
        serviceID = json.get('serviceID')
        print('i got it!' + serviceID)
        payload = {'loginId': serviceID, "reqParams": ["ADMIN_STATUS","OPER_STATUS",'ONT_TX_POWER','ONT_RX_POWER','LASTUPTIME']}
        print(payload)
        # payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        # r = requests.post('http://10.41.56.90:9001/rest/api/reading', json = payload, headers = headers)
        r = requests.post('http://localhost:9001/rest/api/reading', json=payload, headers=headers)
        # val = urllib.unquote(r.url).decode('utf8')
        # print(val)
        print(r.content)
        return r.json()
        # return "restapi_south"

api.add_resource(BarAPI, '/getParam', endpoint='getParam')

if __name__ == '__main__':
    app.secret_key = 'mysecret3'
    # app.run('127.0.0.1', 5001, True)
    app.run('0.0.0.0', 5002, True)