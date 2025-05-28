FROM debian:bookworm

# install dependencies
RUN apt-get update -qq && \
	apt-get install -qq --no-install-recommends \
		build-essential \
		python3 \
		python3-dev \
		python3-pip \
		python3-setuptools \
		python3-wheel \
		libffi-dev \
	> /dev/null && \
	rm -rf /var/cache/apk/*

# build app
RUN mkdir code
WORKDIR /code
COPY requirements.txt /requirements.txt
COPY tests/requirements.txt /requirements.tests.txt

# --break-system-packages to allow pip to install inside of the docker container
RUN pip3 -q install -Ur /requirements.txt --break-system-packages
RUN pip3 -q install -Ur /requirements.tests.txt --break-system-packages

# run app
ENTRYPOINT ["pytest"]
