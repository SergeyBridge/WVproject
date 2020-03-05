FROM python:3.7-alpine3.8
#FROM ubuntu:18.04


RUN apk update
#RUN apt install -qy virtualenv
#RUN . virtualenv/bin/activate


WORKDIR /home/WebVork
COPY claimForecast.py .
VOLUME /home/WebVork

ARG ytarget="None"

ENTRYPOINT ["python", "./claimForecast.py"]
CMD ["--ytarget"]
