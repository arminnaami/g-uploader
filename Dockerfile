FROM alpine:3.7

ENV HOME /root
WORKDIR ${HOME}

COPY requirements.txt ${HOME}/requirements.txt

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN pip3 install -r requirements.txt

RUN apk add --no-cache aria2 && \
    mkdir /root/Downloads

EXPOSE 8000
