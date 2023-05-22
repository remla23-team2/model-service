from flask import Flask, request, jsonify, Response
from flasgger import Swagger
from flask_cors import CORS

import prometheus_client
from prometheus_client import Counter, Gauge, Histogram, Summary
# from prometheus_flask_exporter import PrometheusMetrics

import pickle
import joblib

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from src.preprocessing import process_review
from random import random


app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# metrics = PrometheusMetrics(app)

cv = pickle.load(open('data/models/c1_BoW_Sentiment_Model.pkl', 'rb'))
classifier = joblib.load('data/models/c2_Classifier_Sentiment_Model')

count_predict = 0
averages = []
buffer_predict = []
buffer_label = []

predict_counter = Counter('predictions_counter', 'The total number of model predictions')
model_accuracy = Gauge('model_accuracy', 'Accuracy of the predictions')
feedback_trend = Histogram(
    'feedback_trend', 'How the feedbacks change when time flies', 
    buckets=[5, 10, 15, 20, 25, 30, 35, 40, 45, 50],
    labelnames=['bin']
)

def split_and_average(l, chunk_size):
    """
    This function was helped with ChatGPT initially, but has been modified to fit our needs.
    l: the list of feedbacks, 1 for positive, 0 for negative
    chunk_size: the number of feedbacks to average
    """
    chunks = [l[i:i+chunk_size] for i in range(0, len(l), chunk_size)]
    averages = [sum(chunk)/len(chunk) for chunk in chunks]
    return averages

@app.route('/metrics', methods=['GET'])
def metrics():
    num_correct = sum([int(x == y) for x, y in zip(buffer_predict, buffer_label)])
    accuracy = round(num_correct/len(buffer_label), 2)
    model_accuracy.set(accuracy)

    registry = prometheus_client.CollectorRegistry()
    registry.register(predict_counter)
    registry.register(model_accuracy)
    registry.register(feedback_trend)

    return Response(prometheus_client.generate_latest(registry), mimetype="text/plain")

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict whether a given SMS is Spam or Ham (dumb model: always predicts 'ham').
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                review:
                    type: string
                    example: This is an example of an SMS.
    responses:
      200:
        description: "The result of the classification: 'spam' or 'ham'."
    """
    global count_predict, averages, buffer_predict, buffer_label

    count_predict += 1
    
    predict_counter.inc()
    
    input_data = request.get_json()
    review = input_data.get('review')
    processed_review = process_review(review)
    
    X = cv.transform([processed_review]).toarray()
    result = int(classifier.predict(X)[0])
    if len(buffer_predict) >= 50:
        buffer_predict.pop(0)
    buffer_predict.append(result)

    if len(buffer_predict) % 5 == 0: # we compute the average every 5 predictions
        averages = split_and_average(list(reversed(buffer_predict)), 5)
        if len(averages) >= 10:
            averages.pop(0)
        while len(averages) < 10: # fill in the remaining spots with 0's
            averages.append(0)
        for i, avg in enumerate(averages):
            feedback_trend.labels(bin=i+1).observe(avg)

    # Attach the ground truth to another list to compute the success rate.
    label = input_data.get('ground_truth')
    buffer_label.append(1 if label == 'Positive' else 0)
    
    result = 'Positive' if result == 1 else 'Negative'

    return jsonify({
        "result": result,
        "review": processed_review
    })
   
app.run(host="0.0.0.0", port=8080, debug=True)

