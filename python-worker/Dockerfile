# python-worker/Dockerfile

# Use an official, slim Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's source code into the container
COPY . .

# Expose the port that the Uvicorn server will run on
EXPOSE 8000

# The command to run your FastAPI application when the container launches
CMD ["uvicorn", "api_worker:app", "--host", "0.0.0.0", "--port", "8000"]
