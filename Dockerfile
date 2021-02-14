FROM ubuntu:18.04

LABEL maintainer="andres@kemeny.cl"

RUN apt update -y && apt upgrade -y
RUN apt install -y python3.6 python3-pip

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
