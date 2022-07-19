FROM ubuntu:20.04

WORKDIR /app

COPY install-deps.sh install-deps.sh

COPY requirements.txt requirements.txt

RUN ./install-deps.sh

COPY . .

RUN dvc pull -r origin

RUN chmod +x train.sh
RUN chmod +x classification.sh

CMD [ "/bin/bash" ]