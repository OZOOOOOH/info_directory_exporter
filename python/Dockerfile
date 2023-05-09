FROM python:3.10.11-slim


RUN apt update

COPY ./Pipfile ./Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy --ignore-pipfile

WORKDIR /app
COPY ./python /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/python

CMD ["python3", "custom_exporter.py"]