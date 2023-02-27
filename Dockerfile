FROM dvcorg/cml:latest

WORKDIR /app

COPY . .

RUN dvc pull -r origin

FROM ubuntu:20.04

WORKDIR /app

COPY install-deps.sh install-deps.sh

COPY requirements.txt requirements.txt

RUN chmod +x ./install-deps.sh && ./install-deps.sh

COPY --from=0 /app /app

RUN mkdir /models/

COPY Senti4SD.model /models/Senti4SD.model

RUN dos2unix train.sh
RUN dos2unix classification.sh

RUN chmod +x train.sh
RUN chmod +x classification.sh

CMD [ "/bin/bash" ]