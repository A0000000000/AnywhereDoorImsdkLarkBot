FROM ubuntu:latest
LABEL authors="maoyanluo"
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

WORKDIR /ws

RUN apt update
RUN apt install -y python3-full python3-pip
COPY requirements.txt /ws

RUN python3 -m venv larkbot
RUN source /ws/larkbot/bin/activate && pip3 install -r requirements.txt

COPY src /ws/src

EXPOSE 80

WORKDIR /ws/src

ENTRYPOINT ["/ws/larkbot/bin/python3", "main.py"]