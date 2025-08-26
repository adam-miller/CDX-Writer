FROM python:2.7-slim

WORKDIR /CDX-writer

COPY . .

COPY <<"EOT" requirements.txt
certifi==2021.10.8
chardet==4.0.0
idna==2.10
requests==2.27.1
requests-file==2.1.0
six==1.17.0
surt==0.3.1
tldextract==2.2.3
urllib3==1.26.20
warctools==4.10.0
EOT

RUN pip install virtualenv
RUN virtualenv /opt/cdx_writer
RUN /opt/cdx_writer/bin/pip install -r requirements.txt .

ENTRYPOINT [ "/opt/cdx_writer/bin/cdx_writer" ]