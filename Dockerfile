FROM python:3.12-slim-bookworm

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv && pipenv install --system --deploy

COPY . .

RUN pip install gunicorn

COPY docker-entrypoint.sh .

RUN chmod +x docker-entrypoint.sh

CMD ["./docker-entrypoint.sh"]
