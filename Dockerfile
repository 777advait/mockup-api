FROM python:3.10-slim

WORKDIR /app


RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl tar libltdl-dev&& \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install required dependencies including imagemagick
RUN curl -L -o ImageMagick.tar.gz https://github.com/ImageMagick/ImageMagick/archive/refs/tags/7.1.1-43.tar.gz && \
    tar -xzf ImageMagick.tar.gz && \
    mv ImageMagick-7.1.1-43 ImageMagick-7.1.1 && \
    rm ImageMagick.tar.gz

RUN cd ImageMagick-7.1.1 && \
    ./configure --with-modules && \
    make install && \
    ldconfig /usr/local/lib


# Copy and install requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python", "app.py"]
