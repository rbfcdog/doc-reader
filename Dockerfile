FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt
