# Use the Python 3.7 image
FROM python:3.7

# Set the working directory
WORKDIR /root

# Copy the requirements file to the container
COPY requirements.txt /root/

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the pre-processing function
COPY preprocessing.py /root/

# Copy the application code to the container
COPY app.py /root/

#Download the models
RUN mkdir -p /root/models
RUN curl -L -o /root/models/c1_BoW_Sentiment_Model.pkl https://github.com/remla23-team2/model-training/raw/main/data/models/c1_BoW_Sentiment_Model.pkl
RUN curl -L -o /root/models/c2_Classifier_Sentiment_Model https://github.com/remla23-team2/model-training/raw/main/data/models/c2_Classifier_Sentiment_Model

# Set the entrypoint and default command for the container
ENTRYPOINT ["python"]
CMD ["app.py"]
