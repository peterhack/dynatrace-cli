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

### Setup user for build execution and application runtime
ENV APP_ROOT=/opt/app-root
ENV PATH=${APP_ROOT}/bin:${PATH} HOME=${APP_ROOT}
COPY /usr/bin/ ${APP_ROOT}/bin/
COPY . ${APP_ROOT}
RUN chmod -R u+x ${APP_ROOT}/bin && \
    chgrp -R 0 ${APP_ROOT} && \
    chmod -R g=u ${APP_ROOT} /etc/passwd

### Containers should NOT run as root as a good practice
USER 10001
WORKDIR ${APP_ROOT}

### user name recognition at runtime w/ an arbitrary uid - for OpenShift deployments
ENTRYPOINT [ "uid_entrypoint" ]
VOLUME ${APP_ROOT}/logs ${APP_ROOT}/data
CMD run
