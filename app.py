from flask import Flask, request, jsonify
from flasgger import Swagger
import joblib
from sklearn.feature_extraction.text import CountVectorizer
import pickle
from flask_cors import CORS
import requests
import io

import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()
# from src.preprocessing import pre_process

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

# Load the trained model
cv = pickle.load(open('data/models/c1_BoW_Sentiment_Model.pkl', "rb"))

# Load the Classifier Sentiment Model
classifier = joblib.load('data/models/c2_Classifier_Sentiment_Model')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Make a hardcoded prediction
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
                msg:
                    type: string
                    example: This is an example msg.
    responses:
      200:
        description: Some result
    """
    
    res = {
      "review": "this is a positive or negative review"
    }
    
    return jsonify(res)
   

app.run(host="0.0.0.0", port=8080, debug=True)

