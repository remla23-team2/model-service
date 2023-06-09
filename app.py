from flask import Flask, request, jsonify, Response
from flasgger import Swagger
from flask_cors import CORS

import prometheus_client
from prometheus_client import Counter, Gauge, Histogram, Summary
# from prometheus_flask_exporter import PrometheusMetrics

import pickle
import joblib

import nltk
import time
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
buffer_rating_stars = []
buffer_rating_hearts = []
feedback_counts = [0, 0, 0, 0, 0, 0, 0]

predict_counter = Counter('predictions_counter', 'The total number of model predictions')
model_accuracy = Gauge('model_accuracy', 'Accuracy of the predictions')
feedback_per_day = Histogram(
    'feedback_per_day', 
    'Feedback count for each day of the week', 
    buckets=[0, 1, 2, 3, 4, 5, 6]
)
feedback_summary = Summary('feedback_summary', 'Feedback summary')
average_rating = Gauge('average_rating', 'Average rating of the reviews', ['rating'])

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
    if len(buffer_label) == 0:
        accuracy = 0
    else:
        accuracy = round(num_correct/len(buffer_label), 2)
    model_accuracy.set(accuracy)
    
    if len(buffer_rating_stars) == 0:
        average_rating_value_stars = 0
    else:
        average_rating_value_stars = round(sum(buffer_rating_stars)/len(buffer_rating_stars), 2)
    if len(buffer_rating_hearts) == 0:
        average_rating_value_hearts = 0
    else: 
        average_rating_value_hearts = round(sum(buffer_rating_hearts)/len(buffer_rating_hearts), 2)
    average_rating.labels(rating='stars').set(average_rating_value_stars)
    average_rating.labels(rating='hearts').set(average_rating_value_hearts)

    registry = prometheus_client.CollectorRegistry()
    registry.register(predict_counter)
    registry.register(model_accuracy)
    registry.register(feedback_per_day)
    registry.register(feedback_summary)
    registry.register(average_rating)

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
    global count_predict, averages, buffer_predict, buffer_label, feedback_counts

    count_predict += 1
    
    predict_counter.inc()
    
    input_data = request.get_json()
    review = input_data.get('review')
    processed_review = process_review(review)
    
    # Add the rating to a list to compute the average rating.
    rating = input_data.get('rating')
    rating_type = input_data.get('rating_type')
    if rating_type == 'stars':
        buffer_rating_stars.append(rating)
    else:
        buffer_rating_hearts.append(rating)
    
    X = cv.transform([processed_review]).toarray()
    result = int(classifier.predict(X)[0])
    if len(buffer_predict) >= 50:
        buffer_predict.pop(0)
    buffer_predict.append(result)

    weekday = round(time.time()) % 7  # simulate a different weekday with each request
    feedback_counts[weekday] += 1
    feedback_per_day.observe(weekday)
    
    # Summary: if weekday is a weekend, then 1, else 0. Add it to the summary.
    summary_value = 1 if weekday > 4 else 0
    feedback_summary.observe(summary_value)

    # Attach the ground truth to another list to compute the success rate.
    label = input_data.get('ground_truth')
    buffer_label.append(1 if label == 'Positive' else 0)
    
    result = 'Positive' if result == 1 else 'Negative'

    return jsonify({
        "result": result,
        "review": processed_review,
        "rating": rating,
        "rating_type": rating_type
    })
   
app.run(host="0.0.0.0", port=8080, debug=True)

