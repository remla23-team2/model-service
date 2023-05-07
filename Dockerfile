# Use the Python 3.7 image
FROM python:3.7

# Set the working directory
WORKDIR /root

# Copy the requirements file to the container
COPY requirements.txt /root/

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the application code to the container
COPY app.py /root/

# Set the entrypoint and default command for the container
ENTRYPOINT ["python"]
CMD ["app.py"]
