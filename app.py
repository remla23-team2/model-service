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

countIdx = 0
countSub = 0

@app.route('/', methods=['GET'])
def index():
    global countIdx
    countIdx += 1
    return "<html><body><h1>Index</h1><p>You are visitor {}!</p><a href=\"./sub\">Goto Sub</a></body></html>".format(countIdx)

@app.route('/sub', methods=['GET'])
def sub():
    global countSub
    countSub += 1
    return "<html><body><h1>Sub</h1><p>This is not the main page anymore. Welcome sub-visitor {}!</p><a href=\"./\">Back to Index</a></body></html>".format(countSub)

@app.route('/metrics', methods=['GET'])
def metrics():
    global countIdx, countSub

    m = "# HELP my_random This is just a random 'gauge' for illustration.\n"
    m+= "# TYPE my_random gauge\n"
    m+= "my_random " + str(random()) + "\n\n"

    m+= "# HELP num_requests The number of requests that have been served, by page.\n"
    m+= "# TYPE num_requests counter\n"
    m+= "num_requests{{page=\"index\"}} {}\n".format(countIdx)
    m+= "num_requests{{page=\"sub\"}} {}\n".format(countSub)

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
    input_data = request.get_json()
    review = input_data.get('review')
    processed_review = process_review(review)
    
    X = cv.transform([processed_review]).toarray()
    result = int(classifier.predict(X)[0])
    result = 'Positive' if result == 1 else 'Negative'
    
    return jsonify({
        "result": result,
        "review": processed_review
    })
   
app.run(host="0.0.0.0", port=8080, debug=True)

