FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port (documentation only, actual port comes from $PORT)
EXPOSE ${PORT}

# Use Gunicorn with dynamic port from environment variable
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT} app:app"]
