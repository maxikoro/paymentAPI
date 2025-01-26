FROM python:3.12-slim

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../model.py .
COPY ../main.py .

EXPOSE 8000

CMD [ "fastapi", "dev", "--host", "0.0.0.0", "--port", "8000", "./main.py" ]
