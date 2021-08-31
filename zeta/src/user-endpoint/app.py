import os 
import requests
from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse

app = Flask(__name__)
api = Api(app)

# ENV Variables
SERVICE_KNOWLEDGE_URL = None
POLICY_EVALUATION_SERVICE = None
TRUST_KNOWLEDGE_URL = None

# Checks and initializes env variables required for the service
def init_environment_variables():
    global SERVICE_KNOWLEDGE_URL
    global POLICY_EVALUATION_SERVICE
    global TRUST_KNOWLEDGE_URL

    SERVICE_KNOWLEDGE_URL = os.environ.get('SERVICE_KNOWLEDGE_URL')
    if not SERVICE_KNOWLEDGE_URL:
        raise Exception('SERVICE_KNOWLEDGE_URL not defined')
    
    POLICY_EVALUATION_SERVICE = os.environ.get('POLICY_EVALUATION_SERVICE')
    if not POLICY_EVALUATION_SERVICE:
        raise Exception('POLICY_EVALUATION_SERVICE not defined')

    TRUST_KNOWLEDGE_URL = os.environ.get('TRUST_KNOWLEDGE_URL')
    if not TRUST_KNOWLEDGE_URL:
        raise Exception('TRUST_KNOWLEDGE_URL not defined')

class UserPolicyService(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('policyString')
        parser.add_argument('policyName')
        args= parser.parse_args()

        data = {'policyString': args['policyString'],
                'policyName' : args['policyName']}

        r = requests.post(f'http://{POLICY_EVALUATION_SERVICE}:2000/createPolicy',data=data)
        return {r.status_code}, 200

# This is an optional endpoint. The updateData endpoint should be called by
# the authorization service.
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('data')
        parser.add_argument('endpoint')
        args= parser.parse_args()

        data = {'data': args['data'],
                'endpoint' : args['endpoint']}

        r = requests.post(f'http://{SERVICE_KNOWLEDGE_URL}:2000/updateData',data=data)
        return {r.status_code}, 200

class UserTrustService(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('yaml')
        args= parser.parse_args()

        data = { 'yaml': args['yaml'] }

        r = requests.post(f'http://{TRUST_KNOWLEDGE_URL}:3000/Trust',data=data)
        return {r.status_code}, 200


api.add_resource(UserPolicyService, '/policy')
api.add_resource(UserTrustService, '/trust')

init_environment_variables()
if __name__ == '__main__':    
    app.run(debug=True)
