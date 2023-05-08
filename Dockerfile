FROM python:3.10.11-slim

WORKDIR /custom

RUN apt update

COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv install --system --deploy --ignore-pipfile

COPY custom custom

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/custom

CMD ["python3", "custom/custom_exporter.py"]