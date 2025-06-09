# Dockerfile for the Darwin Gödel Machine (DGM)

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /dgm

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the DGM source code into the container
COPY . .

# Set environment variables (optional, can be overridden in docker-compose)
# Ensures Python output is sent straight to the terminal
ENV PYTHONUNBUFFERED=1

# Define the command to run on container startup
CMD ["python3", "dgm_orchestrator.py"]
