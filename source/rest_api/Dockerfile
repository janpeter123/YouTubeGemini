# Base image: Python
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy your application code to the container
COPY . /app

# Install Python dependencies (if any)
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to execute when the container starts
CMD ["python", "main.py"]
