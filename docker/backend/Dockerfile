FROM debian:10

# install dependencies
RUN apt-get update -qq && \
    apt-get install -y git libjpeg-dev libpq-dev gettext python3 python3-pip


# build app
RUN mkdir code
WORKDIR /code
COPY requirements.txt ./

RUN pip3 install -Ur requirements.txt

# run app
EXPOSE 5000
CMD ["./serve.py"]



