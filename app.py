from flask import Flask, request, Response, jsonify
from src.descriptive.descriptive import Descriptive
from src.predictive import Predictive
from src.min_costs_icu_beds import run_model

app = Flask(__name__)

descriptive = Descriptive()
predictive = Predictive()

@app.route('/', methods=['GET'])
def handle_root():
    response = Response('Welcome to TAIL-OR')
    return response

@app.route('/predict_contamination', methods=['POST'])
def predict_contamination():
    request_data = request.get_json()
    
    horizon = request_data.get("horizon")
    response = predictive.contamination(horizon)
    
    return response

@app.route('/prescriptive', methods=['POST'])
def prescriptive():
    request_data = request.get_json()

    demand = request_data.get("demand")
    equipment_rates = request_data.get("equipment_rates")
    staff_rates = request_data.get("staff_rates")
    consumable_rates = request_data.get("consumable_rates")

    response = run_model(demand, equipment_rates, staff_rates, consumable_rates)

    return response

@app.route('/describe_region', methods=['GET'])
def describe_region():
    response = descriptive.describe_region_statistics()
    
    return response

@app.route('/describe_hospital', methods=['GET'])
def describe_hospital():
    response = descriptive.describe_hospital_statistics()
    
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)