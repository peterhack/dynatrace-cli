FROM python:3

RUN apt-get update && \
pip3 install requests 

COPY ./dtcli.py /opt/dtcli.py

CMD ["bash"]

