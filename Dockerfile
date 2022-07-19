FROM ubuntu:20.04

WORKDIR /app

COPY install-deps.sh install-deps.sh

COPY requirements.txt requirements.txt

RUN chmod +x ./install-deps.sh && ./install-deps.sh

COPY . .

RUN dvc pull -r origin

RUN dos2unix train.sh
RUN dos2unix classification.sh

RUN chmod +x train.sh
RUN chmod +x classification.sh

CMD [ "/bin/bash" ]