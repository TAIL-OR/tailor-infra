from flask import Flask, request, Response
from src.descriptive.descriptive import Descriptive
from src.predictive.predictive import Predictive
from src.prescritive.prescritive import Prescritive

app = Flask(__name__)

descriptive = Descriptive()
predictive = Predictive() 
prescritive = Prescritive()

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)