FROM python:buster

RUN mkdir -p /opt/singnet
COPY . /opt/singnet/snet-sdk-server

WORKDIR /opt/singnet/snet-sdk-server

RUN apt-get update; \
    apt-get install -y libudev-dev libusb-1.0-0-dev

RUN pip install -r requirements.txt

ENTRYPOINT ["/usr/local/bin/python snet-sdk-server"]