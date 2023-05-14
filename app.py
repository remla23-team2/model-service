from flask import Flask, request, jsonify, Response
from flasgger import Swagger
from flask_cors import CORS

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

cv = pickle.load(open('data/models/c1_BoW_Sentiment_Model.pkl', 'rb'))
classifier = joblib.load('data/models/c2_Classifier_Sentiment_Model')

count_predict = 0
averages = []
buffer_predict = []


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
    global count_predict, averages, buffer_predict

    m = "Monitering the webapp:\n"
    m+= "1. Number of feedbacks received (Counter): {}\n".format(count_predict)
    m+= "2. Model Accuracy (Gauge): " + "\n"  # not finished yet
    m += "3. The trend on changing average favorable rates for every 5 Customers (Histogram):\n"
    for i, avg in enumerate(averages):
        m += f"Recent Feedback{i*5}-{i*5+4}: {round(avg, 2)}\n"
    m+= "Feedback list (only for debugging):" + str(buffer_predict) + "\n"
    m+= "4. How does our restaurant perform in the previous months (Summary): "

    return Response(m, mimetype="text/plain")

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
    global count_predict, averages, buffer_predict

    count_predict += 1
    input_data = request.get_json()
    review = input_data.get('review')
    processed_review = process_review(review)
    
    X = cv.transform([processed_review]).toarray()
    result = int(classifier.predict(X)[0])
    if len(buffer_predict) > 50:
        buffer_predict.pop(0)
    buffer_predict.append(result)
    averages = split_and_average(list(reversed(buffer_predict)), 5)
    
    result = 'Positive' if result == 1 else 'Negative'
    
    return jsonify({
        "result": result,
        "review": processed_review
    })
   
app.run(host="0.0.0.0", port=8080, debug=True)

