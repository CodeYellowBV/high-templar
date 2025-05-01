FROM debian:bookworm

# install dependencies
RUN apt-get update -qq && \
    apt-get install -y git libjpeg-dev libpq-dev gettext python3 python3-pip libffi-dev


# build app
RUN mkdir code
WORKDIR /code
COPY requirements.txt ./

# --break-system-packages to allow pip to install inside of the docker container
RUN pip3 install -Ur requirements.txt --break-system-packages

# run app
EXPOSE 5000
CMD ["./serve.py"]



