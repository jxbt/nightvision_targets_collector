FROM ubuntu:24.04

WORKDIR /app

COPY . .

RUN chmod +x install.sh & ./install.sh

RUN chmod +x /app/main.py && ln -s /app/main.py /usr/bin/nightvision_targets_collector
RUN ln -s /app/main.py /usr/bin/nvtc

ENTRYPOINT [ "python3","/app/main.py" ]