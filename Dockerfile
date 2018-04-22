FROM python:3.6.5-alpine3.7
RUN apk add --no-cache curl
WORKDIR /app
ENV PYTHONUNBUFFERED 1
ENV PIPENV_SKIP_VALIDATION 1
RUN pip install pipenv==11.9.0
ADD Pipfile ./
ADD Pipfile.lock ./

RUN apk add --no-cache --virtual build-dependencies build-base && \
    pipenv install --deploy --system --verbose --skip-lock && \
    apk del build-dependencies

ENV LISTEN_PORT 80
EXPOSE 80
ADD . ./
CMD ["python", "-OO", "main.py"]