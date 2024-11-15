FROM python:3.13.0-slim-bullseye

WORKDIR /app
COPY ./app  /app
RUN chmod -x /app

RUN pip3 install --upgrade pip setuptools
RUN pip3 install requests
RUN pip3 install fastapi
RUN pip3 install uvicorn
RUN pip3 install pyyaml 

RUN apt-get update
RUN apt-get install -y procps
RUN apt-get install -y vim
RUN apt-get install -y curl
RUN apt-get -y install git

RUN curl -LO https://github.com/kyverno/kyverno/releases/download/v1.12.0/kyverno-cli_v1.12.0_linux_x86_64.tar.gz
RUN tar -xvf kyverno-cli_v1.12.0_linux_x86_64.tar.gz
RUN rm kyverno-cli_v1.12.0_linux_x86_64.tar.gz

RUN cp ./kyverno /usr/local/bin/kyverno
RUN rm ./kyverno
RUN chmod 777 /usr/local/bin/kyverno 
RUN chmod 777 /app

RUN groupadd -g 1001 -f pvgroup
RUN useradd -u 1001 -g pvgroup -M pvuser 
RUN chown -R pvuser:pvgroup /app
RUN chown -R pvuser:pvgroup /usr/local/bin

USER pvuser

EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["server.py"]

