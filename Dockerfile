FROM python:3.7-alpine3.7

RUN apk add --update \
    jq \
    && pip3 install requests

COPY ./dtcli.py /dtcli/dtcli.py

USER 1000

CMD ["bash"]
