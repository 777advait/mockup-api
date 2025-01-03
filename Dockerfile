FROM python:3.10-slim

WORKDIR ./

# Install required dependencies including imagemagick
RUN apt-get update && \
    apt-get install -y --no-install-recommends imagemagick

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
