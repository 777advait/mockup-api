FROM python:3.10-slim

WORKDIR /app

# Install required dependencies including imagemagick
RUN apt-get update && \
    apt-get install -y --no-install-recommends imagemagick  && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python", "app.py"]
