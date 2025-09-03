FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ping \
    netstat \
    vim \
    nano \
    trace \
    htop
RUN addgroup -S -g 10001 app && adduser -S -D -H -u 10001 -G app app

WORKDIR /home/app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY --chown=app:app ./src/ ./src/
USER app:app

CMD [ "python", "-m", "src" ]

