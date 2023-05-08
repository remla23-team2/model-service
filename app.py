from flask import Flask, request
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
from preprocessing import pre_processing

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

# Load the trained model
cv = pickle.load(open('models/c1_BoW_Sentiment_Model.pkl', "rb"))

# Load the Classifier Sentiment Model
classifier = joblib.load('models/c2_Classifier_Sentiment_Model')
 

@app.route('/', methods=['POST'])
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
    msg = request.get_json().get('msg')
    preprocessed_msg = pre_processing(msg)
    prediction = classifier.predict([preprocessed_msg])
    
    return {
    "review": "this is a positive or negative review" #talk to the group
}
   

app.run(host="0.0.0.0", port=8080, debug=True)

