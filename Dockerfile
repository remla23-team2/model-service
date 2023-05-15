# Use the Python 3.9 image
FROM python:3.9

# Set the working directory
WORKDIR /root/

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Clone the model-training repository
RUN apt-get update && \
    apt-get install -y git && \
    git clone https://github.com/remla23-team11/model-training.git model-training

# Copy the contents from the model-training repository
RUN cp /root/model-training/src /root/src && \
    cp /root/model-training/data /root/data

# Copy the application code to the container
COPY app.py .

EXPOSE 8080

# Set the entrypoint and default command for the container
ENTRYPOINT ["python"]
CMD ["app.py"]
