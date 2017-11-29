
import requests
from flask import Flask, jsonify, make_response
from flask_restful import Api, Resource, reqparse
import csv
import random
import math
import operator
import itertools
import json
from json import dumps
import psycopg2
import psycopg2.extras
from psycopg2._psycopg import DatabaseError
import sys

app = Flask(__name__)
api = Api(app)

# @app.route('/getParam', methods=['GET'])
class BarAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('serviceID', type=str)
        json = parser.parse_args()
        r = requests.get('http://localhost:5002/getParam', params=json)


        #Parsing Data to creating testset and inserting to DB
        loginID = r.json().get('custInfo').get('loginId')
        AccessPort = str(r.json().get('custInfo').get('accessPort'))
        temp_prt = AccessPort.split('-')
        tprt = temp_prt[0]
        rec = r.json().get('lineProfiles')
        pp = rec[0]
        packageName = pp['siebelProfile']

        if temp_prt[4:6] == 'V1':
            access_type = 'VDSL'
        else:
            access_type = 'FTTH'

        # VLAN209
        traffic_rec = r.json().get('trafficProfiles')
        vln1 = traffic_rec[0]
        vlan209 = vln1['vlan']
        stat_vlan209 = vln1['isConfigured']

        # VLAN400
        vln2 = traffic_rec[1]
        vlan400 = vln2['vlan']
        stat_vlan400 = vln2['isConfigured']

        # VLAN500
        vln3 = traffic_rec[2]
        vlan500 = vln3['vlan']
        stat_vlan500 = vln3['isConfigured']

        # VLAN
        vln4 = traffic_rec[3]
        vlan600 = vln4['vlan']
        stat_vlan600 = vln4['isConfigured']


        data = []

        if access_type == 'VDSL':
            attr_rec = r.json().get('attributes')
            upstrem_attn = attr_rec[20]['value']
            upstream_snr = attr_rec[23]['value']
            downstream_attn = attr_rec[5]['value']
            downstream_snr = attr_rec[9]['value']

            if bool(stat_vlan209) == True:
                dt1 = str('Enabled')
            else:
                dt1 = str('Disabled')

            if bool(stat_vlan400) == True:
                dt2 = str('Enabled')
            else:
                dt2 = str('Disabled')

            if bool(stat_vlan500) == True:
                dt3 = str('Enabled')
            else:
                dt3 = str('Disabled')

            if bool(stat_vlan600) == True:
                dt4 = str('Enabled')
            else:
                dt4 = str('Disabled')

            if upstrem_attn <= 20 or upstrem_attn == None:
                if upstream_snr >= 8 or upstream_snr == None:
                    dt5 = str('Good')
                else:
                    dt5  = str('Bad')
            else:
                dt5 = str('Bad')

            if downstream_attn <= 20 or downstream_attn == None:
                if downstream_snr >= 8 or downstream_snr == None:
                    dt6 = str('Good')
                else:
                    dt6  = str('Bad')
            else:
                dt6 = str('Bad')

            data.append(dt1)
            data.append(dt2)
            data.append(dt3)
            data.append(dt4)
            data.append(dt5)
            data.append(dt6)
        else:
            attr_rec = r.json().get('attributes')
            olt_tx_pr = attr_rec[13]['value']
            olt_rx_pr = attr_rec[12]['value']

            if bool(stat_vlan209) == True:
                dt1 = str('Enabled')
            else:
                dt1 = str('Disabled')

            if bool(stat_vlan400) == True:
                dt2 = str('Enabled')
            else:
                dt2 = str('Disabled')

            if bool(stat_vlan500) == True:
                dt3 = str('Enabled')
            else:
                dt3 = str('Disabled')

            if bool(stat_vlan600) == True:
                dt4 = str('Enabled')
            else:
                dt4 = str('Disabled')

            if olt_tx_pr >= -28:
                dt5 = str('Good')
            else:
                dt5 = str('Bad')

            if olt_rx_pr >= -28:
                dt6 = str('Good')
            else:
                dt6 = str('Bad')

            data.append(dt1)
            data.append(dt2)
            data.append(dt3)
            data.append(dt4)
            data.append(dt5)
            data.append(dt6)

        # Test Instance
        testdata = []

        for rec in range(len(data)):

            if data[rec] == 'Enabled':
                testdata.append(int(1))
            elif data[rec] == 'Disabled':
                testdata.append(int(2))
            elif data[rec] == 'Good':
                testdata.append(int(1))
            elif data[rec] == 'Bad':
                testdata.append(int(2))


        # Necessary variables declaration
        filename='testdata.csv'
        trainingSet = []
        testSet = []
        predictions = []

        k = 3

        # Reading data from CSV file (This will be read from Database or operating system folder later)
        with open(filename, 'rb') as csvfile:
            lines = csv.reader(csvfile)
            dataset = list(lines)

            for x in range(len(dataset)):

                for y in range(6):
                    if dataset[x][y] == 'TOS':
                        dataset[x][y] = int(0)
                    elif dataset[x][y] == 'Active' or dataset[x][y] == 'ACTIVE':
                        dataset[x][y] = int(1)
                    elif dataset[x][y] == 'Online':
                        dataset[x][y] = int(1)
                    elif dataset[x][y] == 'Offline':
                        dataset[x][y] = int(2)
                    elif dataset[x][y] == 'Captive':
                        dataset[x][y] = int(3)
                    elif dataset[x][y] == 'Yes':
                        dataset[x][y] = int(1)
                    elif dataset[x][y] == 'No':
                        dataset[x][y] = int(2)
                    elif dataset[x][y] == 'Good':
                        dataset[x][y] = int(1)
                    elif dataset[x][y] == 'Bad':
                        dataset[x][y] = int(2)
                    elif dataset[x][y] == 'Enabled':
                        dataset[x][y] = int(1)
                    elif dataset[x][y] == 'Disable' or 'Disabled':
                        dataset[x][y] = int(2)
                        # dataset[x][y] = float(dataset[x][y])

                trainingSet.append(dataset[x])

        testSet.append(testdata)

        # Distance calculation function (Hamming distance)
        def calculateDistance(instance1, instance2, length):

            distance = 0
            # distanceEculidean = 0

            #  Calculate hamming distance
            for x in range(length):

                if instance1[x] == instance2[x]:
                    distance += 0
                else:
                    distance += 1

            return distance

        def getNeighbors(trainingSet, testInstance, k):
            distances = []
            length = len(testInstance) - 1
            for x in range(len(trainingSet)):
                dist = calculateDistance(testInstance, trainingSet[x], length)
                distances.append((trainingSet[x], dist))
            distances.sort(key=operator.itemgetter(1))
            neighbors = []

            for x in range(k):
                neighbors.append(distances[x][0])

            return neighbors

        # Selecting or making decision

        def getResponse(neighbors):
            classVotes = {}

            for x in range(len(neighbors)):
                response = neighbors[x][-1]

                if response in classVotes:
                    classVotes[response] += 1
                else:
                    classVotes[response] = 1
            sortedVotes = sorted(classVotes.iteritems(),
                                 key=operator.itemgetter(1), reverse=True)


            return sortedVotes[0][0]

        for x in range(len(testSet)):
            neighbors = getNeighbors(trainingSet, testSet[x], k)
            print "Neighbors: ", neighbors
            result = getResponse(neighbors)
            print "Result: ", result
            predictions.append(result)
            print "Predictions: ", predictions

        # Connecting with IDEAS DB
        try:
            conn = psycopg2.connect(host="10.44.28.81", database="ideas", user="postgres", password="postgres")
            conn.set_session(autocommit=True)
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            advisory_class_qry = "SELECT * FROM advisory_output WHERE advisory_class=%s"
            cur.execute(advisory_class_qry, (str(result)))
            advisory_result = cur.fetchone()

            if advisory_result:
                summary = advisory_result['advisory_summary']
                prompt = advisory_result['advisory_prompt']
                inbound = advisory_result['advisory_inbound']
                nextEscalation = advisory_result['advisory_next_escalation']

        except (Exception, psycopg2.DatabaseError) as error:
            print 'Error in IDEAS DB\n'
            print(error)
            sys.exit(1)

        finally:
            if conn is not None:
                conn.close()


        expMatrix = ''

        for i in range(len(testdata)):
            expMatrix += str(testdata[i])

        final_expMatrix = '_______'+ str(expMatrix)

        res = neighbors[0][0:-1]

        matchMatrix = ''

        for i in range(len(res)):
            matchMatrix += str(res[i])

        final_matchMatrix = '_______'+ str(matchMatrix)

        print "Expert Matrix: ", final_expMatrix
        print "Match Matrix: ", final_matchMatrix
        print "Summary: ", summary
        print "Prompt: ", prompt
        print "inbound: ", inbound
        print "escalation: ", nextEscalation

        final_data = {
            'PredictedClass': str(result),
            'ExpertMatrix': str(final_expMatrix),
            'MatchMatrix': str(final_matchMatrix),
            'Summary': str(summary),
            'Prompt': str(prompt),
            'Inbound': str(inbound),
            'NextEscalation': str(nextEscalation)
        }


        return jsonify(final_data)




api.add_resource(BarAPI, '/getParam', endpoint='getParam')

if __name__ == '__main__':
    app.secret_key = 'mysecret2'
    # app.run('127.0.0.1', 5001, True)
    app.run('0.0.0.0', 5001, True)