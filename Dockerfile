FROM python:3.10-slim-bookworm

WORKDIR /app

COPY . /app

# Install system dependencies (awscli NOT needed at runtime, but keeping if required)
RUN apt-get update \
    && apt-get install -y awscli \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
