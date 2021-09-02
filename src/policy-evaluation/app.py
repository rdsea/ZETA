from opa_client.opa import OpaClient
from flask import Flask, request
import json
import os

OPA_SERVICE_NAME = None
app = Flask(__name__)

# Checks and initializes env variables required for the script
def init_environment_variables():

    global OPA_SERVICE_NAME

    OPA_SERVICE_NAME = os.environ.get('OPA_SERVICE_NAME')
    if not OPA_SERVICE_NAME:
        raise Exception('OPA_SERVICE_NAME not defined')

class PolicyEvaluation:
    def __init__(self):
        self.client = OpaClient(host=OPA_SERVICE_NAME, port=8181)
        resp = self.client.check_connection()

        if "Yes" not in resp:
            raise Exception("Not connected", flush=True)
        print("Connected to OPA", flush=True)
        
    def update_policy(self, policyString, policyName) -> bool:
        test_policy = """
        package zeta
             
        import data.zeta_framework.client_1
        default trust_client_1 = false

        trust_client_1 {
            trust := input.trust
            client_1.trust == trust
            client_1.service_name == "edge-inference-server"
            input.time > 10
        }            
        """
        
        
        print(policyString, flush=True)
        self.client.update_opa_policy_fromstring(policyString, policyName)
        if policyName in self.client.get_policies_list():
            return True
        return False

    def update_data(self, data, endpoint) -> bool:
        # endpoint = "testapi/testdata"
        return self.client.update_or_create_opa_data(data, endpoint)
        
    def query_rule(self, data, policy_name, rule) -> bool:
        # data = {"message": "hello"}
        resp =  self.client.check_permission(input_data=data, policy_name=policy_name, rule_name=rule)
        return resp['result']

def handle_returns(resp:bool):
    if resp:
        return '{"success"}'
    return '{"failure"}'

@app.route('/createPolicy', methods=['POST'])
def policy_create():
    try:
        data = json.loads(request.data.decode('ascii'))
        policyString = data["policyString"]
        policyName = data["policyName"]
        r = PolicyEvaluation()
        
        resp = r.update_policy(policyString, policyName)
        return handle_returns(resp)

    except Exception as e:
        print(e, flush=True)
        return '{"failure"}'

@app.route('/updateData', methods=['POST'])
def data_update():
    try:
        data = json.loads(request.data.decode('ascii'))
        
        input_data = data["data"]
        endpoint = data["endpoint"]
        r = PolicyEvaluation()
        resp = r.update_data(input_data, endpoint)

        return handle_returns(resp)
    except Exception as e:
        print(e, flush=True)
        return '{"failure"}'

@app.route('/evaluatePolicy', methods=['POST'])
def policy_evaluate():
    try:
        data = json.loads(request.data.decode('ascii'))
        input_data ={"input" : data["data"]}
        policy_name = data["policy_name"]
        rule = data["rule"]
        r = PolicyEvaluation()
        resp = r.query_rule(input_data, policy_name, rule)
        return str(resp)
    except Exception as e:
        print(e, flush=True)
        return '{"failure"}'

init_environment_variables()

if __name__ == '__main__':
    app.run(debug=True, port=3001, host="0.0.0.0")