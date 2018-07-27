FROM alpine:latest

# NOTE: this was taken and adapted from https://github.com/JoshuaRLi/alpine-python3-pip/blob/master/Dockerfile

RUN apk add --update --no-cache python3 && \
    find / -type d -name __pycache__ -exec rm -r {} +   && \
    rm -r /usr/lib/python*/ensurepip                    && \
    rm -r /usr/lib/python*/lib2to3                      && \
    rm -r /usr/lib/python*/turtledemo                   && \
    rm /usr/lib/python*/turtle.py                       && \
    rm /usr/lib/python*/webbrowser.py                   && \
    rm /usr/lib/python*/doctest.py                      && \
    rm /usr/lib/python*/pydoc.py                        && \
    rm -rf /root/.cache /var/cache /usr/share/terminfo  && \
    pip3 install requests

COPY ./dtcli.py /dtcli/dtcli.py

CMD ["bash"]