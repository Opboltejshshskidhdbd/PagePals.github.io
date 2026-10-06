FROM python:3.10-slim

WORKDIR /app

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# Expose standard HF Space port
EXPOSE 7860

# Run Uvicorn server directly
CMD ["python", "-m", "src.server"]
