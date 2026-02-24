FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install lightweight system dependencies for OpenCV Headless
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY . .

# Render dynamically sets the PORT environment variable.
# We set a default of 10000, which is Render's default HTTP port.
ENV HOST=0.0.0.0
ENV PORT=10000

# Expose the default port
EXPOSE $PORT

# Start the FastAPI application with Uvicorn
CMD ["sh", "-c", "uvicorn main:app --host $HOST --port $PORT"]
