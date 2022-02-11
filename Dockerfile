FROM python:3.9.5-buster

RUN apt-get update && apt-get upgrade -y

#Installing Requirements
RUN apt-get install -y ffmpeg python3-pip opus-tools
RUN apt-get -y install curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_16.x  | bash -
RUN apt-get -y install nodejs

#Updating pip
RUN python3.9 -m pip install -U pip

COPY . .

RUN python3.9 -m pip install -U -r requirements.txt

#Running VCBot
CMD ["python3.9","bot.py"]