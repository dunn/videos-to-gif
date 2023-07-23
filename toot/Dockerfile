FROM python:3.11.4-alpine3.18

RUN mkdir toot
WORKDIR toot

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY toot.py ./

COPY metadata.json ./
COPY gifs ./gifs/

CMD ["python3", "toot.py"]
