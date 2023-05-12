from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from src.preprocessing import process_review

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

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
    
    return jsonify({
        "result": "Positive",
        "review": processed_review
    })
   
app.run(host="0.0.0.0", port=8080, debug=True)

