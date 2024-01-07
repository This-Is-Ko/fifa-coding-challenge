# Based on Dockerfile on docker.com

# Base image
FROM python:3.8

# Set the working dir
WORKDIR /code

# Copy the dependencies file to the working dir
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working dir
COPY src/ .

# Run on container start
CMD [ "python", "./fifa_challenge.py" ]