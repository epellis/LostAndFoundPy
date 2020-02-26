FROM python:latest

WORKDIR /app
COPY requirements.txt ./

RUN apt-get update && apt-get install cron -y
RUN pip install  -r requirements.txt

COPY . .

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh
