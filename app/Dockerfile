# Use a lightweight base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_ENV production

# Create and set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the Flask application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
