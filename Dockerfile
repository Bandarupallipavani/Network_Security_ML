FROM python:3.10-slim-bookworm

WORKDIR /app

COPY . /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y awscli \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
