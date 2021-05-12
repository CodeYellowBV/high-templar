FROM debian:buster-20210408-slim

# install dependencies
RUN apt-get update -qq && \
	apt-get install -qq --no-install-recommends \
		build-essential \
		python3 \
		python3-dev \
		python3-pip \
		python3-setuptools \
		python3-wheel \
	> /dev/null && \
    rm -rf /var/cache/apk/*

# build app
RUN mkdir code
WORKDIR /code

COPY requirements.txt /requirements.txt
COPY tests/requirements.txt /requirements.tests.txt
RUN pip3 -q install -Ur /requirements.txt
RUN pip3 -q install -Ur /requirements.tests.txt

COPY . /code

# run app
CMD ["./tests/run.py"]
