FROM python:3.7-alpine3.7

RUN apk add --update \
    jq \
    && pip3 install requests

### Atomic/OpenShift Labels - https://github.com/projectatomic/ContainerApplicationGenericLabels
LABEL name="dynatrace-cli" \
      maintainer="peter.hack@dynatrace.com" \
      vendor="Dynatrace" \
      version="1.0" \
      release="1" \
      summary="Dynatrace CLI for ACM" \
      description="This app will enable containerized authenticated API platform for DT tenant..." \
### Required labels above - recommended below
      url="https://<tenant>.live.dynatrace.com" \
      io.k8s.description="dtcli" \
      io.k8s.display-name="Starter app" \
      io.openshift.expose-services="" \
      io.openshift.tags="dtcli,dynatrace-cli"

### Containers should NOT run as root as a good practice
USER 10001

### user name recognition at runtime w/ an arbitrary uid - for OpenShift deployments
CMD ['bin/sh']
