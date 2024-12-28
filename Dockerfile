FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y procps curl cron nano && \
    apt-get install -y libxml2-dev libxslt1-dev antiword unrtf poppler-utils tesseract-ocr-rus libjpeg-dev && \
    apt-get clean

RUN pip install --no-cache-dir textract uvicorn fastapi python-multipart pillow-heif

COPY replace_lib/image.py /usr/local/lib/python3.9/site-packages/textract/parsers/image.py

RUN mkdir /app
WORKDIR /app/
COPY *.py /app/

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "main:app"]

EXPOSE 8000
