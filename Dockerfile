
FROM ubuntu:16.04

MAINTAINER ytyng

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-setuptools \
    nginx \
    supervisor \
  && rm -rf /var/lib/apt/lists/*

# for pil
# apt-get install libjpeg-dev
# RUN ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/libjpeg.so

# for ipython
# apt-get install lib32ncurses5-dev

# set locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Python packages
COPY requirements/base.txt /tmp/requirements/base.txt
COPY requirements/production.txt /tmp/requirements/production.txt
RUN pip3 install -r /tmp/requirements/base.txt
RUN pip3 install -r /tmp/requirements/production.txt

# setup all the configfiles
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY conf/nginx-app.conf /etc/nginx/sites-available/default
COPY conf/supervisor-app.conf /etc/supervisor/conf.d/

RUN mkdir /var/log/django

COPY . /var/django/aws-eb-docker-django-skeleton

EXPOSE 80
EXPOSE 443
CMD ["supervisord", "-n"]
