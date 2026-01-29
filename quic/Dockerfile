FROM python:3.11-slim
RUN apt-get update && apt-get install -y gcc python3-dev libssl-dev openssl && rm -rf /var/lib/apt/lists/*
RUN pip install aioquic
WORKDIR /app
COPY quic_test.py .