
import requests
from flask import Flask, jsonify, make_response
from flask_restful import Api, Resource, reqparse
import csv
import random
import math
import operator
import itertools
import json

app = Flask(__name__)
api = Api(app)

# @app.route('/getParam', methods=['GET'])
class BarAPI(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('serviceID', type=str)
        json = parser.parse_args()
        r = requests.get('http://localhost:5002/getParam', params=json)
        print('i got CONTENT='+r.content)

        # payload = {"data": "0,0,3,2,2,2,2,2,2,2,2,2,2"}
        # headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        # r1 = requests.post('http://localhost:9001/dataHandler', json = payload, headers = headers)
        # response = r1.json().get('PredictedClass')

        # Necessary variables declaration
        filename='testcat.csv'
        trainingSet = []
        testSet = []
        predictions = []

        k = 3

        # Dummy test data
        tempdata = {"data": "1,1,1,1,1,1,1,1,1,2,2,2,1"}
        data = map(int, tempdata["data"].split(','))

        # Reading data from CSV file (This will be read from Database later)
        with open(filename, 'rb') as csvfile:
            lines = csv.reader(csvfile)
            dataset = list(lines)

            for x in range(len(dataset)):

                for y in range(13):
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

        testSet.append(data)

        # Distance calculation function (Hamming distance)
        def calculateDistance(instance1, instance2, length):

            distance = 0
            # distanceEculidean = 0

            #  Calculate hamming distance
            for x in range(length):

                if x == 2:
                    if instance1[x] == instance2[x]:
                        distance += 0
                    else:
                        distance += 2

                else:
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

        # return "local_engine2"
        return result



api.add_resource(BarAPI, '/getParam', endpoint='getParam')

if __name__ == '__main__':
    app.secret_key = 'mysecret2'
    # app.run('127.0.0.1', 5001, True)
    app.run('0.0.0.0', 5001, True)