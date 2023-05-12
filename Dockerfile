# Use the Python 3.9 image
FROM python:3.9

# Set the working directory
WORKDIR /root/

# Copy the requirements file to the container
COPY requirements.txt /root/

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the pre-processing function
COPY preprocessing.py /root/

# Copy the application code to the container
COPY app.py /root/

# Set the entrypoint and default command for the container
ENTRYPOINT ["python"]
CMD ["app.py"]
