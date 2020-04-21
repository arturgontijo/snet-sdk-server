FROM python:buster

ENV server_dir="/opt/singnet/snet-sdk-server"

RUN apt-get update; \
    apt-get install -y libudev-dev libusb-1.0-0-dev

RUN cd /tmp; \
    curl -sL https://deb.nodesource.com/setup_10.x -o nodesource_setup.sh; \
    bash nodesource_setup.sh; \
    apt-get install -y nodejs; \
    rm -f nodesource_setup.sh

RUN cd /opt; \
    git clone https://github.com/singnet/snet-cli.git; \
    cd snet-cli; \
    ./packages/snet_cli/scripts/blockchain install; \
    pip install -e ./packages/sdk

RUN mkdir -p "${server_dir}"

COPY . "${server_dir}"

WORKDIR "${server_dir}"

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "snet-sdk-server"]