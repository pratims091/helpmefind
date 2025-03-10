FROM python:3.9-slim-buster

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv && pipenv install --system --deploy

COPY . .

RUN adduser -D myuser
USER myuser

RUN pip install gunicorn

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
