from flask import Flask, request
from flask_restful import Resource, Api
import psycopg2
import jwt
import os
import requests
from datetime import datetime, timedelta
from enum import Enum
from helpers.custom_logger import CustomLogger


app = Flask(__name__)
api = Api(app)
logger = CustomLogger().get_logger()


PRIVATE_KEY = None
PUBLIC_KEY = None
TRUST_SERVICE_NAME = None
POLICY_EVAL_SERVICE_NAME = None
 
class ServiceDatabaseHandler:
    def __init__(self):
        #Connect to db
        self.conn = psycopg2.connect(f"postgres://service-knowledge:password@service-knowledge")
        self.cur = self.conn.cursor()
        self.cur.execute('SELECT version()')
        db_version = self.cur.fetchone()
        logger.info(f"Connected to {db_version}")
        self.query = """
        INSERT INTO elasticity_token_info (service_name, target_service_name, capabilities, token)
        VALUES (%s, %s, %s, %s)
        """

    def __del__(self):
        try:
            # Clean up the cursor before destroying the object.
            self.cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

    def save_to_db(self, service_name, capabilities, target_service_name, token):
        self.cur.execute(self.query, (service_name, target_service_name, capabilities, token))
        self.conn.commit()

 
class TrustLevel(Enum):
    NONE = 4
    LOW = 3
    MEDIUM = 2
    HIGH=1

# Checks and initializes env variables required for the script
def init_environment_variables():
    read_private_key()
    read_public_key()

    global TRUST_SERVICE_NAME
    global POLICY_EVAL_SERVICE_NAME

    TRUST_SERVICE_NAME = os.environ.get('TRUST_SERVICE_NAME')
    if not TRUST_SERVICE_NAME:
        raise Exception('TRUST_SERVICE_NAME not defined')

    POLICY_EVAL_SERVICE_NAME = os.environ.get('POLICY_EVAL_SERVICE_NAME')
    if not POLICY_EVAL_SERVICE_NAME:
        raise Exception('POLICY_EVAL_SERVICE_NAME not defined')


def read_public_key():
    global PUBLIC_KEY
    with open("keys/ec_public.pem", "r") as reader:
        PUBLIC_KEY = str(reader.read())
    if PUBLIC_KEY is None:
        raise Exception("Encountered problem while reading public key")
    

def read_private_key():
    global PRIVATE_KEY
    with open("keys/private.pem", "r") as reader:
        PRIVATE_KEY = str(reader.read())
    if PRIVATE_KEY is None:
        raise Exception("Encountered problem while reading private key")
    
class GetAuthToken(Resource):
    def getResponse(self, data, message=None):
        if message == None:
            return {
                'status': 'success',
                'data' : {
                    'token': data
                },
                'message': message
            }
        else:
            return {
                'status': 'failure',
                'data' : None,
                'message' : message
            }

    @staticmethod
    def generateJWTTokenClaims(service_name, expiry, claims):
        # Add capabilities to reflect what this JWT token can do 
        # So service name and capabilities
        return {
            "exp": datetime.utcnow() + timedelta(hours=int(expiry)),
            "nbf": datetime.utcnow(),
            "aud": [f"tefa:{service_name}"],
            "type": "auth_token",
            "cf": claims
        }

    def generateToken(self, service_name, expiry, claims):
        token_claims = GetAuthToken.generateJWTTokenClaims(service_name, expiry, claims)
        token = jwt.encode(token_claims, PRIVATE_KEY, algorithm="ES256")
        return token

    def get(self):
        service_name = request.args.get('name')
        expiry = request.args.get('expiry')
        claims = request.args.get('claims')
        logger.info(f"recieved a auth token request for service {service_name}")

        if service_name is None or expiry is None or claims is None:
            return self.getResponse(data=None, message="Missing information")
        token = self.generateToken(service_name, expiry, claims)
        logger.info(f"Generated an auth token for service {service_name}")
        return  self.getResponse(data=token), 200
    
class GetElasticityToken(Resource):
    def getResponse(self, data=None, message=None):
        if message == None:
            return {
                'status': 'success',
                'data' : {
                    'token': data
                },
                'message': message
            }
        else:
            return {
                'status': 'failure',
                'data' : None,
                'message' : message
            }

    @staticmethod
    def generateJWTTokenClaims(service_name, expiry, claims, value_allowed, target_service_name):
        # Add capabilities to reflect what this JWT token can do 
        # So service name and capabilities
        return {
            "exp": datetime.utcnow() + timedelta(minutes=int(expiry)),
            "nbf": datetime.utcnow(),
            "aud": [f"tefa:{service_name}"],
            "type": "elasticity_token",
            "cf": claims,
            "value_allowed": value_allowed,
            "target_service": target_service_name
        }

    def generateToken(self, service_name, expiry, claims, value_allowed, target_service_name):
        token_claims = GetElasticityToken.generateJWTTokenClaims(service_name, expiry, claims, value_allowed, target_service_name)
        token = jwt.encode(token_claims, PRIVATE_KEY, algorithm="ES256")
        return token

    def check_valid_capabilities(self, decoded, claims):
        requested = claims.split(",")
        authorized = decoded["cf"].split(",")
        return set(requested) <= set(authorized)


    def get(self):
        service_name = request.args.get('name')
        expiry = request.args.get('expiry')
        auth_token = request.args.get('auth_token')
        claims = request.args.get('claims')
        value_requested = request.args.get('value')
        target_service_name = request.args.get('target')

        if service_name is None or auth_token is None:
            return self.getResponse(data=None, message="Missing information")

        try:
            # The following are checked: time, audience, authenticity
            decoded = jwt.decode(auth_token, PUBLIC_KEY, audience=f"tefa:{service_name}", algorithms="ES256")
        except Exception as e:
            print(e)
            return self.getResponse(data=None, message="Error trying to verify the auth token"), 200

        if not self.check_valid_capabilities(decoded, claims):
            return self.getResponse(data=None, message="Error trying to verify the claims"), 200

        time = datetime.utcnow().minute % 42
        print(time, value_requested)
        # Call trust service 
        try:
            r = requests.get(f'http://{TRUST_SERVICE_NAME}:3000/ConfidenceScore?time={time}&required_resource={value_requested}')
            response = r.json()
            trust_level = TrustLevel[response['data']['trust-level'][11:].upper()]
        except Exception as e:
            print(e)
            return self.getResponse(data=None, message="Error calculating trust level"), 200

        policyData = {
                    "data": {
                                "trust": trust_level.name,
                                "service_name": target_service_name,
                                "time": 23
                            },
                    "policy_name": "client_1_policy", #todo: connect to DB 
                    "rule":"trust_client_1"
                    }

        # Evaluate policy
        policy_resp = requests.post(f"http://{POLICY_EVAL_SERVICE_NAME}:3001/evaluatePolicy", json = policyData)

        if not bool(policy_resp.text):
            return self.getResponse(data=None, message="Policy Evaluation rejected"), 200

        token = self.generateToken(service_name, expiry, claims, value_requested, target_service_name)
        # save into db
        db.save_to_db(service_name, claims, target_service_name, token)

        return  self.getResponse(data=token), 200 

init_environment_variables()
db = ServiceDatabaseHandler()


api.add_resource(GetAuthToken, '/authtoken')
api.add_resource(GetElasticityToken, '/elasticitytoken')

if __name__ == '__main__':
    app.run(debug=True, port=4000)