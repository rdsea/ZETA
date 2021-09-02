import trustcalculator.gp_regression as trust_algorithm
import yaml
import numpy as np
from sklearn.preprocessing import minmax_scale
from flask import Flask, request
from flask_restful import Resource, Api
from enum import Enum

CONFIDENCE_SCALE = 100

app = Flask(__name__)
api = Api(app)

class TrustLevel(Enum):
    NONE = 4
    LOW = 3
    MEDIUM = 2
    HIGH=1

#Aux function - only for testing/graph purposes
def read_and_clean_data():
    tmp = np.genfromtxt("clean_values.csv", delimiter=",")
    container_stress_test_array = minmax_scale(tmp[1:, 4]/(1024*1024))*(CONFIDENCE_SCALE)
    size_t = container_stress_test_array.shape[0]
    return container_stress_test_array, size_t

def load_yaml_config():
    conf = {}
    with open("trust_config.yaml", 'r') as stream:
        try:
            conf = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise Exception("no valid yaml")
    return conf

class GetConfidenceScore(Resource):
    def getEnumString(self, score):
        return str(TrustLevel(score))
    def getResponse(self, data, message=None):
        print(self.getEnumString(data))
        if message == None:
            return {
                'status': 'success',
                'data' : {
                    'trust-level': self.getEnumString(data)
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
        time = int(request.args.get('time'))
        required_resource = int(request.args.get('required_resource'))

        conf = load_yaml_config()
        trust_algorithm.set_calculation_parameters(conf, CONFIDENCE_SCALE)

        container_stress_test_array, size_t = read_and_clean_data()
        gp = trust_algorithm.train_model(container_stress_test_array, size_t)
        conf = trust_algorithm.predict(gp, size_t)
        value = trust_algorithm.get_confidence_level(conf, (time, required_resource))
        print(value)    
        return  self.getResponse(data=value), 200 

api.add_resource(GetConfidenceScore, '/ConfidenceScore')


if __name__ == '__main__':
    app.run(debug=True, port=3000)