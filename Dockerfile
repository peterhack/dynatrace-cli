FROM python:3.7-alpine3.7

RUN apk add --update \
    jq \
    && pip3 install requests

### Containers should NOT run as root as a good practice
USER 10001

CMD bash
