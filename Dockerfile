FROM python:3.8-slim-buster

# Install PostgreSQL development files
RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /py-docker

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
    