FROM python:3.10-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Render uses the PORT environment variable
EXPOSE 7860
CMD ["python", "-m", "src.server"]
