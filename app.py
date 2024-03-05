from flask import Flask, request, Response, jsonify
from src.descriptive.descriptive import Descriptive
from src.predictive import Predictive

app = Flask(__name__)

descriptive = Descriptive()
#predictive = Predictive()

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
    doctor_per_beds = request_data.get("doctor_per_beds")
    nurses_per_beds = request_data.get("nurses_per_beds")
    tech_nurses_per_beds = request_data.get("nurses_per_beds")

    oximeter_per_beds = request_data.get("oximeter_per_beds")
    electrocardiogram_per_beds = request_data.get("electrocardiogram_per_beds")
    fan_per_beds = request_data.get("fan_per_beds")

    atracurium_per_beds = request_data.get("atracurium_per_beds")
    midazolam_per_beds = request_data.get("midazolam_per_beds")
    rocuronium_per_beds = request_data.get("rocuronium_per_beds")



    response = ...
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