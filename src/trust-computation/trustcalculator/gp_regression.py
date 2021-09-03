import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from sklearn.preprocessing import RobustScaler, minmax_scale

CONFIDENCE_SCALE = 100
NOISE_ADDITION = 10/CONFIDENCE_SCALE
NOISE_BOUNDARIES = 1e-1
TRUST_MULTIPLIER = 20
LINESPACE_NUM = 10
ACCURACY = 10

def set_calculation_parameters(conf, confidence_scale):
    global TRUST_MULTIPLIER
    global NOISE_BOUNDARIES
    global ACCURACY
    global CONFIDENCE_SCALE 
    CONFIDENCE_SCALE = confidence_scale
    parameters = conf['parameters']

    TRUST_MULTIPLIER = int(parameters['trust-sensitivity'])

    if (parameters['noise'] == 'low'):
        NOISE_BOUNDARIES = 0.01
    if (parameters['noise'] == 'medium'):
        NOISE_BOUNDARIES = 0.1
    if (parameters['noise'] == 'high'):
        NOISE_BOUNDARIES = 0.7

    if (parameters['accuracy'] == 'low'):
        ACCURACY = 5
    if (parameters['accuracy'] == 'medium'):
        ACCURACY = 10
    if (parameters['accuracy'] == 'high'):
        ACCURACY = 20
    

def add_noise(training_set):
    noise = np.random.normal(0, NOISE_ADDITION, size=training_set.shape[0])
    training_set += noise
    return training_set


def train_model(container_stress_test_array, size_t):
    X = np.atleast_2d(np.linspace(0, size_t - 1, size_t)).T

    y = add_noise(container_stress_test_array)
    print(NOISE_ADDITION, NOISE_BOUNDARIES)
    kernel = RBF(100, (1e-1, 1e2)) + WhiteKernel(noise_level=NOISE_ADDITION, noise_level_bounds=(1e-10, NOISE_BOUNDARIES))
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=ACCURACY)
    gp.fit(X, y)
    return gp

def predict(gp, size_t):
    x = np.atleast_2d(np.linspace(0, size_t - 1, (size_t - 1)*LINESPACE_NUM)).T
    y_pred, sigma = gp.predict(x, return_std=True)
    conf = build_confidence_dictionary(y_pred, sigma)
    return conf

def build_confidence_dictionary(y_pred, sigma):
    val = {}
    for idx in range(len(y_pred)):
        val[idx] = (y_pred[idx], sigma[idx]) 
    return val

def get_confidence_level(confidence_dict, value_to_predict):
    x, y = value_to_predict[0], value_to_predict[1]
    x = x * LINESPACE_NUM
    print(x, y)
    regressed_values = confidence_dict[x] 
    if regressed_values[0] - (1.9600 * regressed_values[1] * 1 * TRUST_MULTIPLIER) <= y <= regressed_values[1] + (1.9600 * regressed_values[1] * 1 * TRUST_MULTIPLIER):
        return 1
    if regressed_values[0] - (1.9600 * regressed_values[1] * 2 * TRUST_MULTIPLIER) <= y <= regressed_values[1] + (1.9600 * regressed_values[1] * 2 * TRUST_MULTIPLIER):
        return 2
    if regressed_values[0] - (1.9600 * regressed_values[1] * 4 * TRUST_MULTIPLIER) <= y <= regressed_values[1] + (1.9600 * regressed_values[1] * 4 * TRUST_MULTIPLIER):
        return 3
    
    return 4
