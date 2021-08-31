import os 
import requests
import psycopg2
from helpers.custom_logger import CustomLogger
import json
from flask import Flask, request
from flask_restful import Resource, Api
from flask_restful import reqparse
from helpers.swagger import SwaggerBluprint

app = Flask(__name__)
api = Api(app)

logger = CustomLogger().get_logger()
class ServiceDatabaseHandler:
    def __init__(self):
        #Connect to db
        self.conn = psycopg2.connect(f"postgres://service-knowledge:password@service-knowledge")
        self.cur = self.conn.cursor()
        self.cur.execute('SELECT version()')
        db_version = self.cur.fetchone()
        logger.info(f"Connected to {db_version}")
        self.query = """
        INSERT INTO authentication_token_info (service_name, capabilities, token)
        VALUES (%s, %s, %s)
        """

    def __del__(self):
        try:
            # Clean up the cursor before destroying the object.
            self.cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)

    def save_to_db(self, service_name, capabilities, token):
        self.cur.execute(self.query, (service_name, capabilities, token))
        self.conn.commit()


swagger = SwaggerBluprint()
swagger_blueprint, swagger_url = swagger.get_swaggerui_blueprint()

app.register_blueprint(swagger_blueprint, url_prefix=swagger_url)

# ENV Variables
AUTH_SERVICE_NAME = None
db = ServiceDatabaseHandler()
# Checks and initializes env variables required for the service
def init_environment_variables():
    global AUTH_SERVICE_NAME

    AUTH_SERVICE_NAME = os.environ.get('AUTH_SERVICE_NAME')
    if not AUTH_SERVICE_NAME:
        raise Exception('AUTH_SERVICE_NAME not defined')


class AuthenticationTokenService(Resource):
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

    def get(self):
        service_name = request.args.get('name')
        capabilities = request.args.get('capabilities')
        expiry = request.args.get('expiry')
        logger.info(f"Recieved auth token request for service name: {service_name}")

        if service_name is None:
            return self.getResponse(data=None, message="No Service Name")

        r = requests.get(f'http://{AUTH_SERVICE_NAME}:4000/authtoken?name={service_name}&claims={capabilities}&expiry={expiry}', timeout=2)
        response = r.json()

        if response['status'] == 'failure':
            return self.getResponse(data=None, message="Failed to generate auth token")
        logger.info(f"Generated auth token for service name: {service_name}")
        #insert into service knowledge
        db.save_to_db(service_name, capabilities, json.dumps(response['data']['token']))
        logger.info(f"Saved to DB the token for service anem: {service_name}")
        return  self.getResponse(data=response['data']['token']), 200

class ElasticityTokenService(Resource):
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
    def get(self):
        try:
            service_name = request.args.get('name')
            expiry = request.args.get('expiry')
            auth_token = request.args.get('auth_token')
            claims = request.args.get('claims')
            value_requested = request.args.get('value')
            target_service_name = request.args.get('target')
        except Exception as e:
            return self.getResponse(data=None, message="Paramter missing"), 200
        
        r = requests.get(f'http://{AUTH_SERVICE_NAME}:4000/elasticitytoken?name={service_name}&claims={claims}&expiry={expiry}&value={value_requested}&target={target_service_name}&auth_token={auth_token}', timeout=2)
        response = r.json()

        if response['status'] == 'failure':
            return self.getResponse(data=None, message="Failed to generate elasticity token")
        logger.info(f"Generated elasticity token for service name: {service_name}")
        return  self.getResponse(data=response['data']['token']), 200


api.add_resource(ElasticityTokenService, '/elasticity')
api.add_resource(AuthenticationTokenService, '/authentication')

init_environment_variables()
if __name__ == '__main__':    
    app.run(debug=True)
    conn = psycopg2.connect(f"postgres://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_URI}")