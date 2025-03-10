FROM python:3.12-slim-bookworm

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv && pipenv install --system --deploy

COPY . .

RUN pip install gunicorn

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
