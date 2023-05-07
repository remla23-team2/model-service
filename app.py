from flask import Flask, request
from flasgger import Swagger
import joblib
from sklearn.feature_extraction.text import CountVectorizer
import pickle
from flask_cors import CORS

import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()

app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

# Load the trained model

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
    return {
    "review": "this is a positive or negative review"
}

app.run(host="0.0.0.0", port=8080, debug=True)

