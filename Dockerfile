# Dockerfile for the DGM Agent

# Use a specific Python version for reproducibility.
FROM python:3.11-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the dependency definition file.
COPY requirements.txt .

# Install the Python dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the DGM application source code into the container.
COPY . .

# Define the command to run when the container starts.
# The agent will begin its evolutionary loop immediately.
CMD ["python", "dgm_agent.py"]
