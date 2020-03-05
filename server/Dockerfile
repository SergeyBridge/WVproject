FROM python:3.7-alpine3.8

# usage: sudo docker run --rm -p 80:80 sergeybridge/webvork_grader

RUN apk add bash

WORKDIR /home/WebVork

COPY server.py .

EXPOSE 80

ENTRYPOINT ["python", "./server.py"]
