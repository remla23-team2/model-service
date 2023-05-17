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
    git clone https://github.com/remla23-team2/model-training.git /root/model-training

# Copy the contents from the model-training repository
RUN cp -r /root/model-training/src /root/src && \
    cp -r /root/model-training/data /root/data

# Copy the application code to the container
COPY app.py .
COPY data data
COPY src src

EXPOSE 8080

# Set the entrypoint and default command for the container
ENTRYPOINT ["python"]
CMD ["app.py"]
